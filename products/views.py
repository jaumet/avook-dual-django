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
from .models import Product, Title, TitleTranslation
from django.db import models
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
        lang_code = self.request.LANGUAGE_CODE[:2]
        return Title.objects.prefetch_related(
            models.Prefetch(
                "translations",
                queryset=TitleTranslation.objects.filter(language_code=lang_code),
                to_attr="translated",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        titles = context['object_list']
        titles_with_status = self.get_titles_with_status(titles)

        titles_by_level = {}
        for item in titles_with_status:
            level = item['title'].level
            if level not in titles_by_level:
                titles_by_level[level] = []
            titles_by_level[level].append(item)

        context['titles_by_level'] = titles_by_level
        return context


def player_view(request, machine_name):
    lang_code = request.LANGUAGE_CODE.upper()
    json_path = os.path.join(settings.BASE_DIR, 'static', 'audios.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return render(request, 'products/player.html', {'error': 'audios.json not found or is invalid'})

    audios_list = data.get('AUDIOS', [])
    audios_map = {item['machine_name']: item for item in audios_list}
    title_data = audios_map.get(machine_name)

    if not title_data:
        return render(request, 'products/player.html', {'error': 'Title not found'})

    text_versions = title_data.get('text_versions', [])
    title_info = None

    # Find the requested language in text_versions
    for version in text_versions:
        if version.get('lang', '').upper() == lang_code:
            title_info = version
            break

    # Fallback to English if requested language is not found
    if not title_info:
        for version in text_versions:
            if version.get('lang', '').upper() == 'EN':
                title_info = version
                break

    # If still not found, fallback to the first available language
    if not title_info and text_versions:
        title_info = text_versions[0]

    # If no text versions exist at all
    if not title_info:
        title_info = {'human-title': machine_name, 'description': ''}

    # Get all available languages from text_versions
    languages = [v.get('lang') for v in text_versions if 'lang' in v]

    context = {
        'machine_name': machine_name,
        'human_title': title_info.get('human-title', machine_name),
        'description': title_info.get('description', ''),
        'languages': languages,
    }

    return render(request, 'products/player.html', {'title': context})


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
