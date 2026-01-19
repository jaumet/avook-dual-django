import json
import logging
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from products.models import Product, UserPurchase

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

        # Determinar l'URL de l'API de PayPal (Sandbox o Live)
        # Aquí assumim que l'entorn es pot determinar a partir de DJANGO_DEBUG
        if settings.DEBUG:
            paypal_api_url = "https://api-m.sandbox.paypal.com/v1/notifications/verify-webhook-signature"
        else:
            paypal_api_url = "https://api-m.paypal.com/v1/notifications/verify-webhook-signature"

        # Obtenir un token d'accés de PayPal
        token_url = paypal_api_url.replace("/v1/notifications/verify-webhook-signature", "/v1/oauth2/token")
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
        if not purchase_units:
            raise ValueError("No s'han trobat 'purchase_units' al payload.")

        # Assumim que la SKU conté el product.machine_name
        product_sku = purchase_units[0].get('items', [{}])[0].get('sku')
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
