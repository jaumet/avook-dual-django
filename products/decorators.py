from functools import wraps
from django.conf import settings

def paypal_csp_decorator(view_func):
    """
    Applies a specific, more permissive Content Security Policy (CSP) required
    for the PayPal JS SDK to function correctly on the checkout page.

    This decorator *replaces* the default site-wide CSP with one tailored for
    PayPal, including 'unsafe-inline' for scripts and specific PayPal domains
    for scripts, images, iframes, and connections.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)

        # Define a specific CSP for the PayPal checkout view
        paypal_csp = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "https://www.paypal.com",
                "https://www.sandbox.paypal.com",
                "https://www.paypalobjects.com",
                "'unsafe-inline'"  # Required by PayPal SDK
            ],
            "style-src": [
                "'self'",
                "https://*.paypalobjects.com",
                "https://*.paypal.com",
                "'unsafe-inline'"
            ],
            "img-src": [
                "'self'",
                "https://*.paypal.com",
                "https://*.paypalobjects.com",
                "data:",
                "blob:"  # Required for certain PayPal elements
            ],
            "connect-src": [
                "'self'",
                "https://www.sandbox.paypal.com",
                "https://c.sandbox.paypal.com",
                "https://www.paypal.com",
                "https://c.paypal.com"
            ],
            "frame-src": [
                "'self'",
                "https://www.paypal.com",
                "https://www.sandbox.paypal.com"
            ],
            "object-src": ["'none'"],
        }

        # Format the CSP dictionary into a header string
        csp_string = "; ".join([f"{key} {' '.join(value)}" for key, value in paypal_csp.items()])

        # Set the specific CSP header for this view's response
        response['Content-Security-Policy'] = csp_string

        return response
    return _wrapped_view
