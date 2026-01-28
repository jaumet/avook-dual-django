import logging
import requests
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import PendingPayment

logger = logging.getLogger(__name__)


def get_paypal_access_token():
    try:
        token_url = f"{settings.PAYPAL_API_URL}/v1/oauth2/token"
        logger.info(f"PayPal token URL: {token_url}")

        response = requests.post(
            token_url,
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
            },
            data={"grant_type": "client_credentials"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("access_token")

    except Exception as e:
        logger.error(f"Error obtaining PayPal access token: {e}")
        return None


def create_payment_resource(
    product_name,
    price,
    machine_name,
    user_id,
    return_url,
    product_id,
    description=""
):
    if price is None:
        logger.error("PayPal: price is None")
        return None

    price_str = f"{Decimal(price):.2f}"

    access_token = get_paypal_access_token()
    if not access_token:
        logger.error("PayPal: could not obtain access token")
        return None

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "custom_id": str(user_id),
                "description": description or product_name,
                "amount": {
                    "currency_code": "EUR",
                    "value": price_str,
                },
            }
        ],
        "application_context": {
            "return_url": return_url,
            "cancel_url": return_url,
        },
    }

    try:
        order_url = f"{settings.PAYPAL_API_URL}/v2/checkout/orders"
        logger.info(f"Creating PayPal order at {order_url}")

        order_resp = requests.post(
            order_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )

        order_resp.raise_for_status()
        data = order_resp.json()

    except Exception as e:
        logger.error(f"PayPal order creation failed: {e}")
        return None

    paypal_order_id = data.get("id")

    if paypal_order_id:
        try:
            User = get_user_model()
            user = User.objects.get(pk=user_id)

            PendingPayment.objects.create(
                paypal_order_id=paypal_order_id,
                user=user,
                product_id=product_id,
                status="pending",
            )

            logger.info(f"Created PendingPayment for {paypal_order_id}")

        except Exception as e:
            logger.error(f"Error creating PendingPayment: {e}")

    for link in data.get("links", []):
        if link.get("rel") == "approve":
            return link.get("href")

    logger.error("No PayPal approval link found")
    return None


def capture_paypal_order(order_id):
    """
    Captures an approved PayPal order.
    Returns the response data if successful, None otherwise.
    """
    access_token = get_paypal_access_token()
    if not access_token:
        logger.error(f"PayPal Capture: could not obtain access token for order {order_id}")
        return None

    try:
        capture_url = f"{settings.PAYPAL_API_URL}/v2/checkout/orders/{order_id}/capture"
        logger.info(f"Capturing PayPal order at {capture_url}")

        response = requests.post(
            capture_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )

        response.raise_for_status()
        data = response.json()
        logger.info(f"PayPal order {order_id} captured successfully.")
        return data

    except Exception as e:
        logger.error(f"PayPal order capture failed for {order_id}: {e}")
        return None
