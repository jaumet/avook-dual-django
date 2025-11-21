from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProductForm, SignUpForm
from .models import Product
from .utils import load_titles_grouped_by_level


class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('titles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marketing_title'] = 'Audiovook Dual — Aprèn llengües escoltant històries'
        context['marketing_subtitle'] = (
            'Escolta narracions combinades per millorar la comprensió i la pronunciació'
        )
        titles_by_level = load_titles_grouped_by_level()
        context['packages'] = [
            {
                'product': product,
                'titles': titles_by_level.get(product.level, []),
            }
            for product in context['products']
        ]
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

<<<<<<< ours
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        titles_by_level = load_titles_grouped_by_level()
        context['package_titles'] = titles_by_level.get(self.object.level, [])
=======
    def get_queryset(self):
        return super().get_queryset().prefetch_related('titles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['package_titles'] = self.object.titles.all()
>>>>>>> theirs
        return context


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_message = 'Producte creat correctament'
    success_url = reverse_lazy('home')


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_message = 'Producte actualitzat'
    success_url = reverse_lazy('home')


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')
    success_message = 'Compte creat! Ja pots iniciar sessió.'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
