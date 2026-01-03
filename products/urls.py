from django.urls import path
from .views import (
    CatalogView,
    ProductListView,
    ProductCreateView,
    ProductDetailView,
    ProductUpdateView,
    player_view,
    title_create,
    title_update,
    CartView,
    add_to_cart,
)

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('player/<slug:machine_name>/', player_view, name='player'),
    path('product/nou/', ProductCreateView.as_view(), name='product_create'),
    path('product/<pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<pk>/editar/', ProductUpdateView.as_view(), name='product_update'),
    path('title/nou/', title_create, name='title_create'),
    path('title/<pk>/editar/', title_update, name='title_update'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
]
