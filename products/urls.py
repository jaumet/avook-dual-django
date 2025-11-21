from django.urls import path
from .views import ProductCreateView, ProductDetailView, ProductUpdateView

app_name = 'products'

urlpatterns = [
    path('nou/', ProductCreateView.as_view(), name='create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', ProductUpdateView.as_view(), name='update'),
]
