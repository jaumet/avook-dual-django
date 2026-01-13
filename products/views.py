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
        # Prefetch translations and related packages
        return Product.objects.prefetch_related(
            'translations',
            'packages__titles'
        ).order_by('price')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context['products']
        language_code = self.request.LANGUAGE_CODE

        for product in products:
            # Get the specific translation for the current language
            product.translation = product.translations.filter(language_code=language_code).first()
            # Fallback to the first available translation if none match
            if not product.translation:
                product.translation = product.translations.first()

            # Get titles with status for each package
            for package in product.packages.all():
                package.titles_with_status = self.get_titles_with_status(package.titles.all())

        context['products'] = products
        context['PAYPAL_CLIENT_ID_LIVE'] = settings.PAYPAL_CLIENT_ID_LIVE
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
        titles_with_status = self.get_titles_with_status(titles)

        # Group titles by level using data from audios.json
        titles_by_level = {}
        for item in titles_with_status:
            level = item['json_info']['levels']
            if level not in titles_by_level:
                titles_by_level[level] = []
            titles_by_level[level].append(item)
        context['titles_by_level'] = titles_by_level

        # Prepare data for the filters
        json_path = os.path.join(settings.BASE_DIR, 'static', 'AUDIOS', 'audios.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                audios_data = json.load(f).get('AUDIOS', [])
        except (FileNotFoundError, json.JSONDecodeError):
            audios_data = []

        lang_code = self.request.LANGUAGE_CODE[:2].upper()
        collections = set()
        durations = set()
        languages = set()
        ages_list = set()

        for audio in audios_data:
            # Add all available languages for the language filter
            for version in audio.get('text_versions', []):
                if version.get('lang'):
                    languages.add(version['lang'])

            # Add other filters based on the current language
            for version in audio.get('text_versions', []):
                if version.get('lang', '').upper() == lang_code:
                    if version.get('colection'):
                        collections.add(_(version['colection']))
                    if version.get('duration'):
                        durations.add(_(version['duration']))
                    if version.get('ages'):
                        ages_list.add(_(version['ages']))

        context['collections'] = sorted(list(collections))
        context['durations'] = sorted(list(durations))
        context['languages'] = sorted(list(languages))
        context['ages_list'] = sorted(list(ages_list))

        # Pass the titles_with_status to the main context
        context['titles_with_status'] = titles_with_status
        return context


def player_view(request, machine_name):
    title = get_object_or_404(Title, machine_name=machine_name)

    mixin = TitleContextMixin()
    mixin.request = request

    # Pass the entire title_info to the template
    titles_with_status = mixin.get_titles_with_status([title])

    if not titles_with_status:
        return render(request, 'products/player.html', {'error': 'Title not found'})

    title_info = titles_with_status[0]
    json_info = title_info.get('json_info', {})

    # Add all text_versions to json_info
    json_path = os.path.join(settings.BASE_DIR, 'static', 'AUDIOS', 'audios.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            audios_data = json.load(f).get('AUDIOS', [])
    except (FileNotFoundError, json.JSONDecodeError):
        audios_data = []

    audios_map = {item['machine_name']: item for item in audios_data}
    title_data = audios_map.get(machine_name, {})
    json_info['text_versions'] = title_data.get('text_versions', [])

    level = json_info.get('levels')

    if not level:
        return render(request, 'products/player.html', {'error': 'Title configuration is missing.'})

    transcripts = {}
    text_versions = json_info.get('text_versions', [])

    for version in text_versions:
        lang = version.get('lang')
        json_file_name = version.get('json_file')

        if lang and json_file_name:
            detailed_json_path = os.path.join(settings.BASE_DIR, 'static', 'AUDIOS', level, json_file_name)
            try:
                with open(detailed_json_path, 'r', encoding='utf-8') as f:
                    detailed_data = json.load(f)
                    transcripts[lang] = detailed_data
            except (FileNotFoundError, json.JSONDecodeError):
                # You might want to log this error
                pass

    if not transcripts:
        return render(request, 'products/player.html', {'error': 'Could not load any title data.'})

    context = {
        'title': json_info,
        'transcripts': transcripts,
        'audio_path_prefix': f"/static/AUDIOS/{level}/{machine_name}/"
    }

    return render(request, 'products/player.html', context)


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
