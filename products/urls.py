from django.urls import path
from .views import (
    ProductCreateView,
    ProductDetailView,
    ProductUpdateView,
    title_create,
    title_update,
)

app_name = 'products'

urlpatterns = [
    path('product/nou/', ProductCreateView.as_view(), name='product_create'),
    path('product/<pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<pk>/editar/', ProductUpdateView.as_view(), name='product_update'),
    path('title/nou/', title_create, name='title_create'),
    path('title/<pk>/editar/', title_update, name='title_update'),
]
