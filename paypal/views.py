import json
import logging
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import strip_tags
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from post_office.utils import send_templated_email
from django.utils.dateparse import parse_datetime
from dateutil.relativedelta import relativedelta

from products.models import Product, UserPurchase, UserAccess
from .services import create_payment_resource, capture_paypal_order, get_paypal_access_token
from .models import PendingPayment

# Configuració del logging
logger = logging.getLogger(__name__)

def verify_paypal_signature(request):
    """
    Verifica la signatura del webhook de PayPal utilitzant l'API de PayPal.
    """
    try:
        auth_algo = request.headers.get('Paypal-Auth-Algo')
        cert_url = request.headers.get('Paypal-Cert-Url')
        transmission_id = request.headers.get('Paypal-Transmission-Id')
        transmission_sig = request.headers.get('Paypal-Transmission-Sig')
        transmission_time = request.headers.get('Paypal-Transmission-Time')
        webhook_id = settings.PAYPAL_WEBHOOK_ID
        event_body = request.body.decode(request.encoding or 'utf-8')

        if not all([auth_algo, cert_url, transmission_id, transmission_sig, transmission_time]):
            logger.error("Capçaleres de verificació de PayPal incompletes.")
            return False

        # Construir el payload per a la verificació
        verification_payload = {
            "auth_algo": auth_algo,
            "cert_url": cert_url,
            "transmission_id": transmission_id,
            "transmission_sig": transmission_sig,
            "transmission_time": transmission_time,
            "webhook_id": webhook_id,
            "webhook_event": json.loads(event_body),
        }

        # Utilitzar el servei existent per obtenir el token
        access_token = get_paypal_access_token()
        if not access_token:
            logger.error("No s'ha pogut obtenir el token d'accés per verificar la signatura.")
            return False

        # Enviar la petició de verificació a PayPal
        paypal_verify_url = f"{settings.PAYPAL_API_URL}/v1/notifications/verify-webhook-signature"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        verify_response = requests.post(paypal_verify_url, headers=headers, json=verification_payload, timeout=10)
        verify_response.raise_for_status()

        verification_status = verify_response.json().get('verification_status')
        if verification_status == 'SUCCESS':
            logger.info("Verificació de la signatura de PayPal amb èxit.")
            return True
        else:
            logger.warning(f"La verificació de la signatura de PayPal ha fallat amb l'estat: {verification_status}")
            return False

    except Exception as e:
        logger.error(f"Error durant la verificació de la signatura de PayPal: {e}")
        return False

@csrf_exempt
@require_POST
def paypal_webhook(request):
    """
    Gestiona els webhooks entrants de PayPal com a única font de veritat.
    """
    # 1. Verificar la signatura del webhook
    if not verify_paypal_signature(request):
        logger.warning("Petició de webhook de PayPal amb signatura invàlida.")
        return HttpResponseBadRequest("Signatura invàlida.")

    # 2. Processar el payload
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Error en llegir el payload JSON del webhook.")
        return HttpResponseBadRequest("Payload invàlid.")

    # 3. Comprovar el tipus d'event (NOMÉS els requerits)
    event_type = payload.get('event_type')
    relevant_events = [
        'PAYMENT.CAPTURE.COMPLETED',
        'PAYMENT.CAPTURE.DENIED',
        'PAYMENT.CAPTURE.REFUNDED'
    ]

    if event_type not in relevant_events:
        logger.info(f"Webhook rebut amb event no rellevant: {event_type}. S'ignora.")
        return HttpResponse(status=200)

    # 4. Extreure la informació rellevant
    try:
        resource = payload.get('resource', {})
        paypal_capture_id = resource.get('id')

        # Cercar paypal_order_id en links si no és a supplementary_data
        supplementary_data = resource.get('supplementary_data', {})
        paypal_order_id = supplementary_data.get('related_ids', {}).get('order_id')

        if not paypal_order_id:
            for link in resource.get('links', []):
                if link.get('rel') == 'up' and '/orders/' in link.get('href', ''):
                    paypal_order_id = link.get('href').split('/orders/')[-1]
                    break

        payment_date_str = resource.get('create_time')
        custom_id = resource.get('custom_id')
        amount = resource.get('amount', {}).get('value')
        currency = resource.get('amount', {}).get('currency_code')

        logger.info(f"Processant webhook {event_type}. Order: {paypal_order_id}, Capture: {paypal_capture_id}, CustomID: {custom_id}, Amount: {amount} {currency}")

    except Exception as e:
        logger.error(f"Error en extreure dades del payload del webhook: {e}")
        return HttpResponseBadRequest("Dades del payload incompletes o malformades.")

    if not paypal_order_id:
        logger.warning(f"No s'ha pogut determinar paypal_order_id per a l'event {event_type}")
        return HttpResponse(status=200)

    # 5. Processar segons el tipus d'event de forma atòmica
    try:
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            with transaction.atomic():
                # Localitzar PendingPayment per paypal_order_id amb bloqueig
                pending_payment = PendingPayment.objects.select_for_update().filter(paypal_order_id=paypal_order_id).first()

                if not pending_payment:
                    logger.warning(f"No s'ha trobat cap pagament pendent per a paypal_order_id: {paypal_order_id}")
                    return HttpResponse(status=200)

                user = pending_payment.user
                product = pending_payment.product

                # Idempotència: comprovar si ja existeix la compra
                purchase_exists = UserPurchase.objects.filter(
                    Q(paypal_order_id=paypal_order_id) | Q(paypal_capture_id=paypal_capture_id)
                ).exists()

                if not purchase_exists:
                    # Mark PendingPayment as PAID
                    pending_payment.status = 'paid'
                    pending_payment.save()

                    # Data de pagament
                    paid_at = parse_datetime(payment_date_str) if payment_date_str else timezone.now()
                    if not paid_at: paid_at = timezone.now()

                    # Crear UserPurchase
                    UserPurchase.objects.create(
                        user=user,
                        user_email=user.email,
                        product=product,
                        paypal_order_id=paypal_order_id,
                        paypal_capture_id=paypal_capture_id,
                        paid_at=paid_at,
                        payment_provider="paypal",
                        status="completed"
                    )
                    logger.info(f"Creada UserPurchase per a l'usuari {user.id} i producte {product.machine_name}.")

                    # Activar en UserAccess
                    expiry_date = None
                    if product.duration:
                        expiry_date = paid_at + relativedelta(months=product.duration)

                    UserAccess.objects.update_or_create(
                        user=user,
                        product=product,
                        defaults={
                            'active': True,
                            'activated_at': paid_at,
                            'expiry_date': expiry_date
                        }
                    )
                    logger.info(f"Producte {product.machine_name} activat per a l'usuari {user.id}.")

                    # Enviar correu de confirmació
                    send_purchase_confirmation_email(user, product, paid_at)
                else:
                    logger.info(f"La compra per a l'ordre {paypal_order_id} ja s'havia processat.")

        elif event_type == 'PAYMENT.CAPTURE.DENIED':
            PendingPayment.objects.filter(paypal_order_id=paypal_order_id).update(status='failed')
            logger.info(f"Pagament pendent {paypal_order_id} marcat com a fallit (DENIED).")

        elif event_type == 'PAYMENT.CAPTURE.REFUNDED':
            with transaction.atomic():
                UserPurchase.objects.filter(
                    Q(paypal_order_id=paypal_order_id) | Q(paypal_capture_id=paypal_capture_id)
                ).update(status='refunded')

                pending = PendingPayment.objects.filter(paypal_order_id=paypal_order_id).first()
                if pending:
                    UserAccess.objects.filter(user=pending.user, product=pending.product).update(active=False)

                logger.info(f"Compra retornada i accés desactivat per a l'ordre {paypal_order_id}.")

    except Exception as e:
        logger.error(f"Error durant el processament del webhook {event_type}: {e}")
        return HttpResponse(status=500)

    return HttpResponse(status=200)

def send_purchase_confirmation_email(user, product, paid_at):
    """
    Envia un correu electrònic de confirmació de compra en l'idioma de l'usuari.
    """
    try:
        lang = getattr(user, 'language_code', 'ca')

        context = {
            'user': user,
            'product_name': str(product),
            'payment_date': paid_at.strftime('%d/%m/%Y %H:%M'),
            'purchase_url': f"https://dual.cat/{lang}/accounts/purchases/"
        }

        send_templated_email(
            template_name='purchase_confirmation',
            context=context,
            to_email=user.email,
            language=lang
        )
        logger.info(f"Correu de confirmació enviat a {user.email}")
    except Exception as e:
        logger.error(f"Error en enviar el correu de confirmació: {e}")

def paypal_capture_view(request):
    """
    Captura l'ordre de PayPal després de l'aprovació de l'usuari.
    """
    order_id = request.GET.get('token')

    if not order_id:
        logger.warning("Redirecció d'èxit de PayPal sense 'token'.")
        return redirect('products:product_list')

    logger.info(f"Iniciant captura server-side per a l'ordre: {order_id}")

    capture_data = capture_paypal_order(order_id)

    if capture_data:
        logger.info(f"Ordre {order_id} capturada correctament. Estat: {capture_data.get('status')}")
    else:
        logger.error(f"Error en capturar l'ordre {order_id} server-side.")

    # Sempre renderitzem la pàgina d'èxit, el webhook farà l'activació real
    return render(request, 'products/success.html', {'order_id': order_id})

@login_required
def get_payment_link_view(request, product_id):
    """
    Genera un enllaç de pagament de PayPal per a un producte.
    """
    product = get_object_or_404(Product, pk=product_id)
    lang = request.LANGUAGE_CODE
    product_translation = product.get_translation(lang)
    product_name = product.machine_name
    product_description = ""

    if product_translation:
        product_name = product_translation.name
        product_description = strip_tags(product_translation.description)

    success_url = request.build_absolute_uri(reverse('products:success'))

    payment_link = create_payment_resource(
        product_name=product_name,
        price=product.price,
        machine_name=product.machine_name,
        user_id=request.user.id,
        return_url=success_url,
        product_id=product.id,
        description=product_description
    )

    if payment_link:
        return JsonResponse({'payment_link': payment_link})
    else:
        return JsonResponse({'error': 'No s\'ha pogut crear l\'enllaç de pagament.'}, status=500)
