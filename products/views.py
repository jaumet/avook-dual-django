import json
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib import messages

from .forms import ProductForm, SignUpForm, TitleForm, TitleLanguageForm
from .models import Product, Title, TitleLanguage
from .utils import load_titles_grouped_by_level


class CatalogView(ListView):
    model = Title
    template_name = 'catalog.html'
    context_object_name = 'titles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        titles = Title.objects.prefetch_related('languages').all()

        titles_list = []
        for title in titles:
            languages = list(title.languages.values('language'))
            titles_list.append({
                'id': title.id,
                'machine_name': title.machine_name,
                'human_name': title.human_name,
                'description': title.description,
                'levels': title.levels,
                'languages': languages,
                'ages': title.ages,
                'collection': title.collection,
                'duration': title.duration,
            })

        context['titles_json'] = titles_list
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
