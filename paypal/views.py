import json
import logging
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import strip_tags
from django.db.models import Q
from django.utils import timezone
from products.models import Product, UserPurchase, UserAccess
from .services import create_payment_resource
from .models import PendingPayment
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Configuració del logging
logger = logging.getLogger(__name__)

def verify_paypal_signature(request):
    """
    Verifica la signatura del webhook de PayPal.
    Retorna True si la signatura és vàlida, False en cas contrari.
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

        # Utilitzar la URL de l'API de PayPal definida a la configuració
        paypal_api_url = f"{settings.PAYPAL_API_URL}/v1/notifications/verify-webhook-signature"

        # Obtenir un token d'accés de PayPal
        token_url = f"{settings.PAYPAL_API_URL}/v1/oauth2/token"
        auth_response = requests.post(
            token_url,
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
            headers={"Accept": "application/json", "Accept-Language": "en_US"},
            data={"grant_type": "client_credentials"}
        )
        auth_response.raise_for_status()
        access_token = auth_response.json()['access_token']

        # Enviar la petició de verificació a PayPal
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        verify_response = requests.post(paypal_api_url, headers=headers, json=verification_payload)
        verify_response.raise_for_status()

        verification_status = verify_response.json().get('verification_status')
        if verification_status == 'SUCCESS':
            logger.info("Verificació de la signatura de PayPal amb èxit.")
            return True
        else:
            logger.warning(f"La verificació de la signatura de PayPal ha fallat amb l'estat: {verification_status}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de xarxa durant la verificació de la signatura de PayPal: {e}")
        return False
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error en processar les dades per a la verificació de la signatura: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperat durant la verificació de la signatura de PayPal: {e}")
        return False

@csrf_exempt
@require_POST
def paypal_webhook(request):
    """
    Gestiona els webhooks entrants de PayPal.
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

    # 3. Comprovar el tipus d'event
    event_type = payload.get('event_type')
    relevant_events = [
        'PAYMENT.CAPTURE.COMPLETED',
        'PAYMENT.CAPTURE.DENIED',
        'PAYMENT.CAPTURE.DECLINED',
        'PAYMENT.CAPTURE.REFUNDED'
    ]

    if event_type not in relevant_events:
        logger.info(f"Webhook rebut amb event no rellevant: {event_type}. S'ignora.")
        return HttpResponse(status=200)

    # 4. Extreure la informació rellevant
    try:
        resource = payload.get('resource', {})
        paypal_capture_id = resource.get('id')

        # Extreure paypal_order_id de supplementary_data si existeix
        supplementary_data = resource.get('supplementary_data', {})
        related_ids = supplementary_data.get('related_ids', {})
        paypal_order_id = related_ids.get('order_id')

        # Fallback per a paypal_order_id si no és a supplementary_data
        if not paypal_order_id:
            # En alguns events, l'order_id pot estar en els links o en altres llocs
            for link in resource.get('links', []):
                if link.get('rel') == 'up':
                    # L'enllaç sol ser /v2/checkout/orders/{id}
                    href = link.get('href', '')
                    if '/orders/' in href:
                        paypal_order_id = href.split('/orders/')[-1]
                        break

        payment_date_str = resource.get('create_time')
        custom_id = resource.get('custom_id')

        logger.info(f"Webhook {event_type} rebut. Order: {paypal_order_id}, Capture: {paypal_capture_id}, CustomID: {custom_id}")

    except Exception as e:
        logger.error(f"Error en extreure dades del payload del webhook: {e}. Payload: {payload}")
        return HttpResponseBadRequest("Dades del payload incompletes o malformades.")

    # 5. Localitzar el pagament pendent
    pending_payment = None
    if paypal_order_id:
        pending_payment = PendingPayment.objects.filter(paypal_order_id=paypal_order_id).first()

    if not pending_payment:
        logger.warning(f"No s'ha trobat cap pagament pendent per a paypal_order_id: {paypal_order_id}")
        return HttpResponse(status=200)

    # 6. Processar segons el tipus d'event
    if event_type == 'PAYMENT.CAPTURE.COMPLETED':
        user = pending_payment.user
        product = pending_payment.product

        # Idempotència: comprovar si ja existeix la compra
        purchase_exists = UserPurchase.objects.filter(
            Q(paypal_order_id=paypal_order_id) | Q(paypal_capture_id=paypal_capture_id)
        ).exists()

        if not purchase_exists:
            # Crear UserPurchase
            paid_at = timezone.now()
            if payment_date_str:
                try:
                    from django.utils.dateparse import parse_datetime
                    paid_at = parse_datetime(payment_date_str) or timezone.now()
                except Exception:
                    pass

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
            logger.info(f"S'ha creat una nova UserPurchase per a l'usuari {user.id} i el producte {product.machine_name}.")

            # Calcular expiry_date basat en la durada del producte
            expiry_date = None
            if product.duration:
                from dateutil.relativedelta import relativedelta
                expiry_date = paid_at + relativedelta(months=product.duration)

            # Activar producte en UserAccess
            access, created = UserAccess.objects.update_or_create(
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
            logger.info(f"La compra per a l'ordre {paypal_order_id} ja ha estat processada prèviament.")

    elif event_type in ['PAYMENT.CAPTURE.DENIED', 'PAYMENT.CAPTURE.DECLINED']:
        pending_payment.status = 'failed'
        pending_payment.save()
        logger.info(f"Pagament pendent {paypal_order_id} marcat com a fallit ({event_type}).")

    elif event_type == 'PAYMENT.CAPTURE.REFUNDED':
        # Marcar UserPurchase com a retornada
        UserPurchase.objects.filter(
            Q(paypal_order_id=paypal_order_id) | Q(paypal_capture_id=paypal_capture_id)
        ).update(status='refunded')

        # Desactivar l'accés
        UserAccess.objects.filter(
            user=pending_payment.user,
            product=pending_payment.product
        ).update(active=False)

        logger.info(f"Compra retornada i accés desactivat per a l'ordre {paypal_order_id}.")

    return HttpResponse(status=200)

def send_purchase_confirmation_email(user, product, paid_at):
    """
    Envia un correu electrònic de confirmació de compra en l'idioma de l'usuari.
    """
    try:
        # Idioma de l'usuari (assumim que el guardem o usem el de la sessió si estigués disponible,
        # però en webhook usem el que tinguem a CustomUser si existeix o el per defecte)
        # En aquest projecte CustomUser no té language_code, així que usem settings.LANGUAGE_CODE o algun altre mecanisme.
        # De moment usem 'ca' i 'en' com a exemples.

        # Si tenim un camp language al model CustomUser, l'hauríem d'usar aquí.
        # Com que no el veig clarament, provarem de detectar-lo o usar 'ca' per defecte.
        lang = getattr(user, 'language_code', 'ca')
        if lang not in ['ca', 'en']:
            lang = 'ca'

        subject = "La teva compra s’ha activat a Dual" if lang == 'ca' else "Your purchase has been activated on Dual"
        template_name = f"emails/purchase_confirmed_{lang}.html"

        context = {
            'user': user,
            'product_name': str(product),
            'payment_date': paid_at.strftime('%d/%m/%Y %H:%M'),
            'purchase_url': "https://dual.cat/ca/accounts/purchases/"
        }

        html_message = render_to_string(template_name, context)

        send_mail(
            subject=subject,
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Correu de confirmació enviat a {user.email}")
    except Exception as e:
        logger.error(f"Error en enviar el correu de confirmació: {e}")

@login_required
def get_payment_link_view(request, product_id):
    """
    View that generates a PayPal payment link for a specific product.
    """
    product = get_object_or_404(Product, pk=product_id)

    # Use the product translation if available
    lang = request.LANGUAGE_CODE
    product_translation = product.get_translation(lang)
    product_name = product.machine_name
    product_description = ""

    if product_translation:
        product_name = product_translation.name
        product_description = strip_tags(product_translation.description)

    # Ensure success URL is absolute
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
        # The service already logs the details
        return JsonResponse({'error': 'Could not create PayPal payment link. Check server logs for details.'}, status=500)
