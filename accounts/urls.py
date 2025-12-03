from django.urls import path
from django.contrib.auth import views as auth_views
from .views import ProfileUpdateView, LibraryView, activate_account

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('library/', LibraryView.as_view(), name='library'),
    path('activate/<uuid:token>/', activate_account, name='activate'),
]
