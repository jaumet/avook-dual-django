from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from products.views import HomeView, SignUpView, root_redirect, CookiesView, NoticeView, PrivacyView, RightsView

# Keep non-translated URLs separate
urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/imgs/favicon.ico')),
    path('admin/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', root_redirect, name='root_redirect'),
]

# Add translated URLs using i18n_patterns
urlpatterns += i18n_patterns(
    path('', HomeView.as_view(), name='home'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('legal/cookies/', CookiesView.as_view(), name='cookies'),
    path('legal/notice/', NoticeView.as_view(), name='notice'),
    path('legal/privacy/', PrivacyView.as_view(), name='privacy'),
    path('legal/rights/', RightsView.as_view(), name='rights'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
