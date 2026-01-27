from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (CustomPasswordResetView, ProfileUpdateView,
                    PurchaseHistoryView, UserActivityPDFView, UserActivityView,
                    activate_account, SignUpView)

app_name = 'accounts'

urlpatterns = [
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('purchases/', PurchaseHistoryView.as_view(), name='purchase_history'),
    path('activity/', UserActivityView.as_view(), name='activity'),
    path('activity/pdf/', UserActivityPDFView.as_view(), name='activity_pdf'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('activate/<str:token>/', activate_account, name='activate'),
]
