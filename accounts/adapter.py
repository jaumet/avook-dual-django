import re
import uuid
from django.urls import reverse
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if getattr(user, 'is_first_login', False):
            user.is_first_login = False
            user.save(update_fields=['is_first_login'])
            return reverse('accounts:profile') + "?edit=1"
        return super().get_login_redirect_url(request)

    def generate_unique_username(self, txts, regex=None):
        # Ensure we only use alphanumeric characters to satisfy CustomUser constraints
        clean_txts = [re.sub(r'[^a-zA-Z0-9]', '', t) for t in txts if t]

        # If no valid text is found, use a random string
        if not clean_txts:
            clean_txts = [uuid.uuid4().hex[:8]]

        # Ensure each base username is at least 5 characters long
        final_txts = []
        for t in clean_txts:
            if len(t) < 5:
                t = (t + uuid.uuid4().hex)[:5]
            final_txts.append(t)

        # Use the alphanumeric regex as default
        if not regex:
            regex = r'^[a-zA-Z0-9]+$'

        return super().generate_unique_username(final_txts, regex)
