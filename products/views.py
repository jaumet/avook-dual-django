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
from django.db.models import Q
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from django.urls import reverse
from post_office.utils import send_templated_email
from .forms import ProductForm, SignUpForm, TitleForm, TitleLanguageForm
from .models import Product, Title, TitleLanguage, TranslatableContent
from .utils import load_titles_grouped_by_level
from .mixins import TitleContextMixin


class ProductListView(TitleContextMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products_by_category'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('packages__titles__languages').order_by('price')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset()
        products_by_category = {
            'start': list(products.filter(category='start')),
            'progress': list(products.filter(category='progress')),
            'full_access': list(products.filter(category='full_access')),
        }
        context['products_by_category'] = products_by_category
        context['language_map'] = dict(settings.LANGUAGES)
        for category in products_by_category.values():
            for product in category:
                for package in product.packages.all():
                    package.titles_with_status = self.get_titles_with_status(package.titles.all())
        return context


from .models import HomePageContent

class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('packages__titles')

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


TitleLanguageFormSet = inlineformset_factory(
    Title, TitleLanguage, form=TitleLanguageForm, extra=1, can_delete=True
)

@login_required
def title_create(request):
    if request.method == 'POST':
        form = TitleForm(request.POST)
        formset = TitleLanguageFormSet(request.POST, instance=Title())
        if form.is_valid() and formset.is_valid():
            title = form.save()
            formset.instance = title
            formset.save()
            messages.success(request, 'Títol creat correctament.')
            return redirect('home')
    else:
        form = TitleForm()
        formset = TitleLanguageFormSet(instance=Title())
    return render(request, 'products/title_form.html', {'form': form, 'formset': formset})

@login_required
def title_update(request, pk):
    title = Title.objects.get(pk=pk)
    if request.method == 'POST':
        form = TitleForm(request.POST, instance=title)
        formset = TitleLanguageFormSet(request.POST, instance=title)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Títol actualitzat correctament.')
            return redirect('home')
    else:
        form = TitleForm(instance=title)
        formset = TitleLanguageFormSet(instance=title)
    return render(request, 'products/title_form.html', {'form': form, 'formset': formset})


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')
    success_message = _("Your account has been created successfully! Please check your email to activate your account.")

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
            user.email
        )

        return response


class CatalogView(TitleContextMixin, ListView):
    model = Title
    template_name = 'catalog.html'
    context_object_name = 'titles_with_status'

    def get_queryset(self):
        return Title.objects.prefetch_related('languages').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        titles = context['object_list']

        context['titles_with_status'] = self.get_titles_with_status(titles)

        context['language_map'] = dict(settings.LANGUAGES)
        context['collections'] = sorted(list(titles.values_list('collection', flat=True).distinct()))
        context['durations'] = sorted(list(titles.values_list('duration', flat=True).distinct()))
        context['languages'] = sorted(list(TitleLanguage.objects.filter(title__in=titles).values_list('language', flat=True).distinct()))
        context['ages_list'] = sorted(list(titles.values_list('ages', flat=True).distinct()))
        context['levels'] = sorted(list(titles.values_list('levels', flat=True).distinct()))

        return context


def player_view(request, machine_name):
    title = get_object_or_404(Title, machine_name=machine_name)
    languages = title.languages.all()
    return render(request, 'products/player.html', {'title': title, 'languages': languages})


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
