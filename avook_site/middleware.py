import base64
import os

class CspNonceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
        request.csp_nonce = nonce
        response = self.get_response(request)

        # Make sure the Content-Security-Policy header is set
        if 'Content-Security-Policy' in response:
            # Replace the placeholder with the actual nonce
            response['Content-Security-Policy'] = response['Content-Security-Policy'].replace('nonce-placeholder', f"'nonce-{nonce}'")

        return response
