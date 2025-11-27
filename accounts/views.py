from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView
from products.models import Package
from products.mixins import TitleContextMixin
from .forms import ProfileUpdateForm

User = get_user_model()


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
