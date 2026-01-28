import json

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView, View
from weasyprint import HTML

from post_office.utils import send_templated_email
from products.models import TitleTranslation, UserActivity, UserPurchase

from .forms import CustomPasswordResetForm, ProfileUpdateForm, SignUpForm

User = get_user_model()


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user


class PurchaseHistoryView(LoginRequiredMixin, ListView):
    model = UserPurchase
    template_name = 'accounts/purchase_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        purchases = UserPurchase.objects.filter(user=user).order_by('-purchase_date').select_related('product')

        active_purchases = []
        expired_purchases = []
        now = timezone.now()

        for p in purchases:
            p.product.translation = p.product.get_translation(self.request.LANGUAGE_CODE)
            if p.expiry_date:
                if p.expiry_date > now:
                    p.days_remaining = (p.expiry_date - now).days
                    active_purchases.append(p)
                else:
                    p.days_remaining = 0
                    expired_purchases.append(p)
            else:
                p.days_remaining = None
                active_purchases.append(p)

        context['active_purchases'] = active_purchases
        context['expired_purchases'] = expired_purchases
        return context


def activate_account(request, token):
    try:
        user = User.objects.get(confirmation_token=token)
        user.is_active = True
        user.email_confirmed = True
        user.confirmation_token = None
        user.save()

        # Automatic login
        login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
        messages.success(request, _('Your account has been activated successfully.'))

        if getattr(user, 'is_first_login', False):
            user.is_first_login = False
            user.save(update_fields=['is_first_login'])
            return redirect(reverse('accounts:profile') + "?edit=1")

        return redirect('home')
    except User.DoesNotExist:
        messages.error(request, _('The activation token is invalid or has expired.'))
        return redirect('home')


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')
    success_message = _("Thank you for signing up! We've sent you an email to activate your account.")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        activation_path = reverse('accounts:activate', kwargs={'token': user.confirmation_token})
        domain = self.request.get_host()
        protocol = 'https' if self.request.is_secure() else 'http'
        token_url = f"{protocol}://{domain}{activation_path}"
        context = {'user': user, 'token_url': token_url}
        send_templated_email('account_confirmation', context, user.email, language=self.request.LANGUAGE_CODE)
        return response


class UserActivityMixin:
    def get_annotated_activities(self):
        user = self.request.user
        language_code = self.request.LANGUAGE_CODE
        activities = UserActivity.objects.filter(user=user).select_related('title').order_by('-last_listened_date')
        title_ids = {act.title_id for act in activities}
        if not title_ids:
            return activities
        translations = {t.title_id: t for t in TitleTranslation.objects.filter(title_id__in=title_ids, language_code=language_code)}
        for activity in activities:
            translation = translations.get(activity.title_id)
            activity.title.human_name = translation.human_name if translation else activity.title.machine_name
            activity.listening_time_minutes = round(activity.listening_time.total_seconds() / 60, 1)
        return activities


class UserActivityView(LoginRequiredMixin, UserActivityMixin, ListView):
    model = UserActivity
    template_name = 'accounts/activity.html'
    context_object_name = 'activities'

    def get_queryset(self):
        return self.get_annotated_activities()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities = self.object_list
        language_code = self.request.LANGUAGE_CODE

        lang_pair_data = activities.values('language_pair').annotate(
            total_seconds=Sum('listening_time')
        ).order_by('-total_seconds')

        lang_pair_labels = [item['language_pair'] for item in lang_pair_data]
        lang_pair_values = [item['total_seconds'].total_seconds() / 60 for item in lang_pair_data]

        level_data = activities.values('title__level').annotate(
            count=Count('title', distinct=True)
        ).order_by('title__level')

        bubble_chart_datasets = []
        background_colors = [
            'rgba(255, 99, 132, 0.5)', 'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)', 'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)', 'rgba(255, 159, 64, 0.5)'
        ]

        for i, item in enumerate(level_data):
            color = background_colors[i % len(background_colors)]
            bubble_chart_datasets.append({
                'label': item['title__level'] or 'N/A',
                'data': [{
                    'x': (i * 10) + 5,
                    'y': 5,
                    'r': item['count'] * 5
                }],
                'backgroundColor': color
            })

        timeline_data = activities.annotate(
            date=TruncDate('last_listened_date')
        ).values('date').annotate(
            daily_seconds=Sum('listening_time')
        ).order_by('date')

        timeline_labels = [item['date'].strftime('%Y-%m-%d') for item in timeline_data]
        timeline_values = [item['daily_seconds'].total_seconds() / 60 for item in timeline_data]

        wordcloud_data = activities.values(
            'title_id', 'title__machine_name'
        ).annotate(
            total_time=Sum('listening_time')
        ).order_by('-total_time')

        wc_title_ids = {item['title_id'] for item in wordcloud_data}
        wc_translations = {}
        if wc_title_ids:
            wc_translations_qs = TitleTranslation.objects.filter(
                title_id__in=wc_title_ids,
                language_code=language_code
            )
            wc_translations = {t.title_id: t for t in wc_translations_qs}

        wordcloud_words = [
            {'text': (wc_translations.get(item['title_id']).human_name if wc_translations.get(item['title_id']) else item['title__machine_name']),
             'weight': item['total_time'].total_seconds()}
            for item in wordcloud_data
        ]

        treemap_data = activities.values(
            'title__level', 'language_pair'
        ).annotate(
            total_time=Sum('listening_time')
        ).order_by('title__level', 'language_pair')

        context['chart_data'] = json.dumps({
            'langPairChart': {'labels': lang_pair_labels, 'data': lang_pair_values},
            'bubbleChart': {'datasets': bubble_chart_datasets},
            'timelineChart': {'labels': timeline_labels, 'data': timeline_values},
            'wordCloud': wordcloud_words,
            'treemapData': [
                {
                    'level': item['title__level'],
                    'lang_pair': item['language_pair'],
                    'time': item['total_time'].total_seconds()
                } for item in treemap_data
            ]
        })

        return context


class UserActivityPDFView(LoginRequiredMixin, UserActivityMixin, View):
    def get(self, request, *args, **kwargs):
        activities = self.get_annotated_activities()
        html_string = render_to_string('accounts/activity_pdf.html', {'activities': activities})
        html = HTML(string=html_string)
        response = HttpResponse(html.write_pdf(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="activity_report.pdf"'
        return response
