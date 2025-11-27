from django.urls import path
from django.urls import path
from .views import ProfileUpdateView, LibraryView

app_name = 'accounts'

urlpatterns = [
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('library/', LibraryView.as_view(), name='library'),
]
