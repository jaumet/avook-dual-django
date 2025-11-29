from django.test import TestCase
from django.urls import reverse
from django.utils import translation

class AccountsURLTest(TestCase):
    def test_logout_url_works_with_post(self):
        """
        Verify that the logout URL resolves and redirects as expected on POST.
        """
        # The logout URL is under the 'accounts' namespace and is internationalized
        with translation.override('ca'):
            logout_url = reverse('accounts:logout')

        # Logout should be a POST request for security
        response = self.client.post(logout_url)

        # A successful logout should redirect (HTTP 302)
        self.assertEqual(response.status_code, 302)
