import os
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, TemplateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import json
from django.db.models import Q
from django.http import JsonResponse

from django.urls import reverse
from post_office.utils import send_templated_email
from .forms import ProductForm, SignUpForm, TitleForm
from .models import Product, Title, TranslatableContent
from .utils import load_titles_grouped_by_level
from .mixins import TitleContextMixin


class ProductListView(TitleContextMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'packages__titles', 'translations'
        ).order_by('price')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context['products']

        for product in products:
            for package in product.packages.all():
                package.titles_with_status = self.get_titles_with_status(package.titles.all())
        return context


from .models import HomePageContent

class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('packages__titles', 'translations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = self.request.LANGUAGE_CODE
        content_obj = HomePageContent.objects.first()

        if content_obj:
            context['home_page_content'] = getattr(content_obj, f'content_{lang}', '')
        else:
            context['home_page_content'] = ''
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('translations')


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
    success_message = _("Gràcies per registrar-te! T'hem enviat un correu per activar el teu compte.")

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.object

        # Send confirmation email
        activation_path = reverse('accounts:activate', kwargs={'token': user.confirmation_token})
        domain = self.request.get_host()
        protocol = 'https' if self.request.is_secure() else 'http'
        token_url = f"{protocol}://{domain}{activation_path}"

        context = {
            'user': user,
            'token_url': token_url,
        }

        send_templated_email(
            'account_confirmation',
            context,
            user.email,
            language=self.request.LANGUAGE_CODE
        )

        login(self.request, user)
        return response


class CatalogView(TitleContextMixin, ListView):
    model = Title
    template_name = 'catalog.html'
    context_object_name = 'titles_with_status'

    def get_queryset(self):
        return Title.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        titles = context['object_list']

        context['titles_with_status'] = self.get_titles_with_status(titles)

        context['language_map'] = dict(settings.LANGUAGES)
        context['levels'] = sorted(list(titles.values_list('level', flat=True).distinct()))

        return context


def player_view(request, machine_name):
    title = get_object_or_404(Title, machine_name=machine_name)
    return render(request, 'products/player.html', {'title': title})


def root_redirect(request):
    return redirect('/ca/')


class CookiesView(TemplateView):
    template_name = 'legal/cookies.html'


class NoticeView(TemplateView):
    template_name = 'legal/notice.html'


class PrivacyView(TemplateView):
    template_name = 'legal/privacy.html'


class RightsView(TemplateView):
    template_name = 'legal/rights.html'
