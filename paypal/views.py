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
from products.models import Product, UserPurchase
from .services import create_payment_resource

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
        return HttpResponseForbidden("Signatura invàlida.")

    # 2. Processar el payload
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Error en llegir el payload JSON del webhook.")
        return HttpResponseBadRequest("Payload invàlid.")

    # 3. Comprovar el tipus d'event
    event_type = payload.get('event_type')
    if event_type != 'PAYMENT.CAPTURE.COMPLETED':
        logger.info(f"Webhook rebut amb event no rellevant: {event_type}. S'ignora.")
        return HttpResponse(status=200)

    # 4. Extreure la informació rellevant
    try:
        resource = payload.get('resource', {})
        custom_id = resource.get('custom_id')  # ID de l'usuari Django
        purchase_units = resource.get('purchase_units', [])

        # Support for Payment Links and Buttons API where info might be in the SKU
        product_sku = None
        if purchase_units:
            product_sku = purchase_units[0].get('items', [{}])[0].get('sku')

        # Fallback for SKU location in some webhook versions/types
        if not product_sku:
            # Check if it's in resource/amount/details or somewhere else if needed
            # For Payment Links, it usually ends up in purchase_units[0].items[0].sku
            pass

        if product_sku and '--' in product_sku:
            sku_parts = product_sku.split('--')
            product_sku = sku_parts[0]
            if not custom_id and len(sku_parts) > 1:
                custom_id = sku_parts[1]
                logger.info(f"Extret custom_id de la SKU: {custom_id}")

        if not product_sku:
            raise ValueError("No s'ha trobat la SKU del producte al payload.")

        if not custom_id:
            raise ValueError("No s'ha trobat el 'custom_id' d'usuari al payload.")

        logger.info(f"Processant compra per a l'usuari ID: {custom_id} i producte SKU: {product_sku}")

    except (IndexError, KeyError, ValueError) as e:
        logger.error(f"Error en extreure dades del payload del webhook: {e}. Payload: {payload}")
        return HttpResponseBadRequest("Dades del payload incompletes o malformades.")

    # 5. Lògica de negoci: Crear UserPurchase
    User = get_user_model()
    try:
        user = User.objects.get(pk=custom_id)
        product = Product.objects.get(machine_name=product_sku)

        # Comprovar si la compra ja existeix per evitar duplicats
        if UserPurchase.objects.filter(user=user, product=product).exists():
            logger.warning(f"La compra per a l'usuari {user.id} i el producte {product.machine_name} ja existeix. No es crearà un duplicat.")
        else:
            UserPurchase.objects.create(user=user, product=product)
            logger.info(f"S'ha creat una nova UserPurchase per a l'usuari {user.id} i el producte {product.machine_name}.")

    except User.DoesNotExist:
        logger.error(f"L'usuari amb ID {custom_id} no existeix.")
        return HttpResponseBadRequest(f"Usuari amb ID {custom_id} no trobat.")
    except Product.DoesNotExist:
        logger.error(f"El producte amb machine_name {product_sku} no existeix.")
        return HttpResponseBadRequest(f"Producte amb SKU {product_sku} no trobat.")
    except Exception as e:
        logger.error(f"Error inesperat en crear la UserPurchase: {e}")
        return HttpResponse("Error intern del servidor.", status=500)

    return HttpResponse(status=200)

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
        description=product_description
    )

    if payment_link:
        return JsonResponse({'payment_link': payment_link})
    else:
        return JsonResponse({'error': 'Could not create payment link'}, status=500)
