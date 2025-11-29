import os
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib import messages
from django.db.models import Q

from .forms import ProductForm, SignUpForm, TitleForm, TitleLanguageForm
from .models import Product, Title, TitleLanguage, TranslatableContent
from .utils import load_titles_grouped_by_level
from .mixins import TitleContextMixin


class ProductListView(TitleContextMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('packages__titles__packages')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for product in context['products']:
            for package in product.packages.all():
                package.titles_with_status = self.get_titles_with_status(package.titles.all())
        return context


class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('packages__titles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the current language from the URL prefix
        lang = self.request.LANGUAGE_CODE

        # Fetch all translatable content objects
        content_objects = TranslatableContent.objects.all()

        # Prepare a dictionary to hold the content for the template
        translatable_content = {}
        for item in content_objects:
            # Construct the field name, e.g., 'content_ca'
            field_name = f'content_{lang}'
            # Get the content from the appropriate language field, fallback to 'en' if empty
            content = getattr(item, field_name, '') or getattr(item, 'content_en', '')
            translatable_content[item.key] = content

        context['translatable_content'] = translatable_content
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
    success_message = 'Compte creat! Ja pots iniciar sessió.'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class CatalogView(TitleContextMixin, ListView):
    model = Title
    template_name = 'catalog.html'
    context_object_name = 'titles'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        level = self.request.GET.get('level')
        collection = self.request.GET.get('collection')
        duration = self.request.GET.get('duration')
        lang = self.request.GET.get('lang')
        ages = self.request.GET.get('ages')

        if query:
            queryset = queryset.filter(
                Q(human_name__icontains=query) |
                Q(description__icontains=query)
            )
        if level:
            queryset = queryset.filter(levels=level)
        if collection:
            queryset = queryset.filter(collection=collection)
        if duration:
            queryset = queryset.filter(duration=duration)
        if lang:
            queryset = queryset.filter(languages__language=lang)
        if ages:
            queryset = queryset.filter(ages=ages)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections'] = Title.objects.values_list('collection', flat=True).distinct()
        context['durations'] = Title.objects.values_list('duration', flat=True).distinct()
        context['languages'] = TitleLanguage.objects.values_list('language', flat=True).distinct()
        context['ages_list'] = Title.objects.values_list('ages', flat=True).distinct()
        context['levels'] = Title.objects.values_list('levels', flat=True).distinct()

        context['titles_with_status'] = self.get_titles_with_status(context['titles'])
        return context


def player_view(request, machine_name):
    title = get_object_or_404(Title, machine_name=machine_name)
    languages = title.languages.all()
    return render(request, 'products/player.html', {'title': title, 'languages': languages})


def root_redirect(request):
    return redirect('/ca/')
