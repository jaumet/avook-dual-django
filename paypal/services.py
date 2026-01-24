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

def create_payment_resource(product_name, price, machine_name, user_id, return_url, description=""):
    """
    Creates a payment resource (link) using the PayPal Payment Links and Buttons API.
    Endpoint: POST /v1/checkout/payment-resources
    """
    access_token = get_paypal_access_token()
    if not access_token:
        return None

    try:
        api_url = f"{settings.PAYPAL_API_URL}/v1/checkout/payment-resources"

        # Encode product info and user ID into product_id (SKU)
        # Using __ as separator for the webhook logic
        sku = f"{machine_name}__{user_id}"

        # Ensure price has 2 decimal places and is a string
        formatted_price = "{:.2f}".format(float(price))

        # Sanitize strings to avoid issues with PayPal's schema
        def sanitize(text, length=127):
            if not text: return ""
            # Remove newlines and non-ascii if necessary, but at least truncate
            return str(text).replace("\n", " ").replace("\r", "")[:length].strip()

        # Robust payload strictly following the manual's structure
        payload = {
            "type": "BUY_NOW",
            "integration_mode": "LINK",
            "reusable": "MULTIPLE",
            "return_url": return_url,
            "line_items": [
                {
                    "name": sanitize(product_name),
                    "product_id": sanitize(sku),
                    "description": sanitize(description or product_name),
                    "unit_amount": {
                        "currency_code": "EUR",
                        "value": formatted_price
                    }
                }
            ]
        }

        logger.info(f"Creating PayPal payment resource with payload: {json.dumps(payload)}")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=10)

        if response.status_code != 201:
            logger.error(f"PayPal API error: {response.status_code} - {response.text}")
            return None

        data = response.json()
        payment_link = data.get('payment_link')

        if not payment_link:
            logger.error(f"PayPal response missing payment_link: {data}")
            return None

        return payment_link
    except Exception as e:
        logger.error(f"Error creating PayPal payment resource: {e}")
        return None
