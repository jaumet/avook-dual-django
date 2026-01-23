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
        # Format: machine_name--user_id
        sku = f"{machine_name}--{user_id}"

        # Ensure price has 2 decimal places
        formatted_price = "{:.2f}".format(float(price))

        # PayPal description limit is usually 127 chars
        clean_description = (description or product_name)[:127]

        payload = {
            "type": "BUY_NOW",
            "integration_mode": "LINK",
            "reusable": "MULTIPLE",
            "return_url": return_url,
            "line_items": [
                {
                    "name": product_name,
                    "product_id": sku,
                    "description": clean_description,
                    "unit_amount": {
                        "currency_code": "EUR",
                        "value": formatted_price
                    }
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get('payment_link')
    except Exception as e:
        logger.error(f"Error creating PayPal payment resource: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logger.error(f"PayPal Response: {e.response.text}")
        return None
