import json
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    known_languages = forms.CharField(widget=forms.HiddenInput(), required=False)
    learning_languages = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'known_languages', 'learning_languages']

    def clean_known_languages(self):
        languages = self.cleaned_data.get('known_languages')
        if languages:
            try:
                return json.loads(languages)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for known languages.")
        return []

    def clean_learning_languages(self):
        languages = self.cleaned_data.get('learning_languages')
        if languages:
            try:
                return json.loads(languages)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for learning languages.")
        return []
