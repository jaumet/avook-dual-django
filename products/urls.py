from django.urls import path
from .views import (
    ProductCreateView,
    ProductDetailView,
    ProductUpdateView,
    TitleCreateView,
    TitleUpdateView,
)

app_name = 'products'

urlpatterns = [
    path('product/nou/', ProductCreateView.as_view(), name='product_create'),
    path('product/<pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<pk>/editar/', ProductUpdateView.as_view(), name='product_update'),
    path('title/nou/', TitleCreateView.as_view(), name='title_create'),
    path('title/<pk>/editar/', TitleUpdateView.as_view(), name='title_update'),
]
