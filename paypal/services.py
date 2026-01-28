import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def get_paypal_access_token():
    """
    Obtains an OAuth 2.0 access token from PayPal.
    """
    try:
        token_url = f"{settings.PAYPAL_API_URL}/v1/oauth2/token"
        response = requests.post(
            token_url,
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
            headers={"Accept": "application/json", "Accept-Language": "en_US"},
            data={"grant_type": "client_credentials"},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        logger.error(f"Error obtaining PayPal access token: {e}")
        return None
import os
import requests
import logging
from decimal import Decimal
from .models import PendingPayment
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

def create_payment_resource(product_name, price, machine_name, user_id, return_url, product_id, description=""):
    # VALIDACIÓ
    if price is None:
        logger.error("PayPal: price is None")
        return None

    price_str = f"{Decimal(price):.2f}"

    # MODE
    mode = os.getenv("PAYPAL_MODE")

    if mode == "sandbox":
        base_url = os.getenv("PAYPAL_API_URL_SANDBOX")
        client_id = os.getenv("PAYPAL_CLIENT_ID_SANDBOX")
        secret = os.getenv("PAYPAL_SECRET_SANDBOX")
    elif mode == "live":
        base_url = os.getenv("PAYPAL_API_URL_LIVE")
        client_id = os.getenv("PAYPAL_CLIENT_ID_LIVE")
        secret = os.getenv("PAYPAL_SECRET_LIVE")
    else:
        logger.error("Invalid PAYPAL_MODE")
        return None

    # TOKEN
    token_resp = requests.post(
        f"{base_url}/v1/oauth2/token",
        auth=(client_id, secret),
        data={"grant_type": "client_credentials"},
    )

    if token_resp.status_code != 200:
        logger.error("PayPal token error: %s", token_resp.text)
        return None

    access_token = token_resp.json()["access_token"]

    # 🔑 PAYLOAD CORRECTE
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "custom_id": str(user_id),
                "description": description or product_name,
                "amount": {
                    "currency_code": "EUR",
                    "value": price_str
                }
            }
        ],
        "application_context": {
            "return_url": return_url,
            "cancel_url": return_url
        }
    }

    # CREATE ORDER
    order_resp = requests.post(
        f"{base_url}/v2/checkout/orders",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json=payload,
    )

    if order_resp.status_code != 201:
        logger.error("PayPal order error: %s", order_resp.text)
        return None

    data = order_resp.json()
    paypal_order_id = data.get("id")

    if paypal_order_id:
        try:
            User = get_user_model()
            user = User.objects.get(pk=user_id)
            PendingPayment.objects.create(
                paypal_order_id=paypal_order_id,
                user=user,
                product_id=product_id,
                status='pending'
            )
            logger.info(f"Created PendingPayment for Order ID: {paypal_order_id}")
        except Exception as e:
            logger.error(f"Error creating PendingPayment: {e}")
            # We don't return None here because the PayPal order was successfully created
            # and the user should be able to pay. We'll have to handle the missing record
            # in the webhook if possible, or log it for manual intervention.

    for link in data.get("links", []):
        if link.get("rel") == "approve":
            return link.get("href")

    logger.error("No approval link found")
    return None
