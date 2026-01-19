from functools import wraps
from django.conf import settings

def paypal_csp_decorator(view_func):
    """
    Modifies the Content Security Policy (CSP) for a specific view to make it
    compatible with the PayPal JS SDK.

    This decorator relaxes the 'script-src' directive by removing the
    'nonce-placeholder' and adding "'unsafe-inline'". This is necessary because
    the PayPal SDK dynamically loads scripts and does not support the nonce-based
    CSP approach implemented in CspNonceMiddleware.

    This decorator is tightly coupled to the existing CSP setup and relies on:
    - `settings.SECURE_CONTENT_SECURITY_POLICY` being a dictionary.
    - `avook_site.middleware.CspNonceMiddleware` using 'nonce-placeholder'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)

        # Start with the default CSP from settings
        csp = settings.SECURE_CONTENT_SECURITY_POLICY.copy()

        # Modify script-src for PayPal
        script_src = csp.get("script-src", [])

        # Remove nonce-placeholder if it exists
        if "nonce-placeholder" in script_src:
            script_src.remove("nonce-placeholder")

        # Add 'unsafe-inline' to allow PayPal's inline scripts
        if "'unsafe-inline'" not in script_src:
            script_src.append("'unsafe-inline'")

        csp["script-src"] = script_src

        # Format the CSP dictionary into a string
        csp_string = "; ".join([f"{key} {' '.join(value)}" for key, value in csp.items()])

        # Set the header
        response['Content-Security-Policy'] = csp_string

        return response
    return _wrapped_view
