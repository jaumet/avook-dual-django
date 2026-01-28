from django.urls import path
from django.views.generic import TemplateView
from paypal.views import paypal_capture_view
from .views import (
    CatalogView,
    ProductListView,
    ProductCreateView,
    ProductDetailView,
    ProductUpdateView,
    player_view,
    ProductTestsView,
)

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('success/', paypal_capture_view, name='success'),
    path('player/<slug:machine_name>/', player_view, name='player'),
    path('product/nou/', ProductCreateView.as_view(), name='product_create'),
    path('product/<pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<pk>/editar/', ProductUpdateView.as_view(), name='product_update'),
    path('<str:machine_name>/tests/', ProductTestsView.as_view(), name='product_tests'),
]
