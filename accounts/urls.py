from django.urls import path, include
from .views import ProfileUpdateView, LibraryView, activate_account

app_name = 'accounts'

urlpatterns = [
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('library/', LibraryView.as_view(), name='library'),
    path('activate/<uuid:token>/', activate_account, name='activate'),
    path('', include('django.contrib.auth.urls')),
]
