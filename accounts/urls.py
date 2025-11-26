from django.urls import path
from .views import ProfileView, LibraryView

app_name = 'accounts'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('library/', LibraryView.as_view(), name='library'),
]
