import os
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from products.models import Package

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


class LibraryView(LoginRequiredMixin, ListView):
    model = Package
    template_name = 'accounts/library.html'
    context_object_name = 'packages'

    def get_queryset(self):
        user = self.request.user
        # Get free packages and packages owned by the user, remove duplicates
        return (Package.objects.filter(is_free=True) | user.packages.all()).distinct().prefetch_related('titles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_packages_ids = set(self.request.user.packages.values_list('id', flat=True))

        for package in context['packages']:
            titles_with_status = []
            for title in package.titles.all():
                # Determine status
                status = ''
                if package.is_free:
                    status = 'FREE'
                elif package.id in user_packages_ids:
                    status = 'PREMIUM_OWNED'
                else:
                    # This case shouldn't be reached with the current queryset logic,
                    # but it's here as a fallback.
                    status = 'PREMIUM_NOT_OWNED'

                # Determine image URL
                image_path = f"AUDIOS/{title.machine_name}/{title.machine_name}.png"
                image_fullpath = os.path.join(settings.STATICFILES_DIRS[0], image_path)
                image_url = ''
                if os.path.exists(image_fullpath):
                    image_url = os.path.join(settings.STATIC_URL, image_path)
                else:
                    image_url = os.path.join(settings.STATIC_URL, "imgs/anonymous-cover.png")

                titles_with_status.append({'title': title, 'status': status, 'image_url': image_url})

            package.titles_with_status = titles_with_status

        return context
