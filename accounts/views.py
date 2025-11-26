import os
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from products.models import Package
from products.mixins import TitleContextMixin

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


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
