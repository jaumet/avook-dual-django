
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView
from products.models import Package
from products.mixins import TitleContextMixin
from .forms import ProfileUpdateForm
from django.shortcuts import redirect
from django.contrib import messages
from post_office.utils import send_templated_email

User = get_user_model()
logger = logging.getLogger(__name__)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user


class LibraryView(LoginRequiredMixin, TitleContextMixin, ListView):
    model = Package
    template_name = 'accounts/library.html'
    context_object_name = 'packages'

    def get_queryset(self):
        user = self.request.user
        # Get free packages and packages owned by the user, remove duplicates
        return (Package.objects.filter(is_free=True) | user.packages.all()).distinct().prefetch_related('titles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for package in context['packages']:
            package.titles_with_status = self.get_titles_with_status(package.titles.all())
        return context


def activate_account(request, token):
    try:
        user = User.objects.get(confirmation_token=token)
        user.is_active = True
        user.email_confirmed = True
        user.confirmation_token = None
        user.save()
        messages.success(request, 'El teu compte ha estat activat correctament. Ara pots iniciar sessió.')
        return redirect('accounts:login')
    except User.DoesNotExist:
        messages.error(request, 'El token d\'activació és invàlid o ha expirat.')
        return redirect('home')


class CustomPasswordResetView(PasswordResetView):
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        send_templated_email(
            'password_reset',
            context,
            to_email,
            from_email
        )


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Error saving new password for user {form.user.username}: {e}")
            # Reraise the exception to maintain the original behavior
            raise
