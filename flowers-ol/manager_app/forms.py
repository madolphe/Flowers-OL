from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Layout, Row, Submit
from django import forms
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import ParticipantProfile


class SignInForm(forms.Form):
    """
    Class to generate a form for logging page.
    """
    username = forms.CharField(label=_("Nom d'utilisateur"),
                               widget=forms.TextInput(attrs={'placeholder': _("Nom d'utilisateur")}))
    password = forms.CharField(label=_("Mot de passe"),
                               widget=forms.PasswordInput(attrs={'placeholder': _('Mot de passe')}))
    fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Se connecter')))


class SignUpForm(forms.ModelForm):
    '''Class to generate a form for sign up page'''
    username = forms.CharField(label=_('Nom d\'utilisateur (ou prolific ID)'),
                               widget=forms.TextInput(attrs={'placeholder': _('Nom d\'utilisateur (ou prolific ID)')}))
    password = forms.CharField(label=_('Mot de passe'),
                               widget=forms.PasswordInput(attrs={'placeholder': _('Mot de passe')}))
    password_confirm = forms.CharField(label=_('Confirmer le mot de passe'),
                                       widget=forms.PasswordInput(attrs={'placeholder': _('Mot de passe')}))
    fields = ['username', 'password', 'password_confirm']
    field_order = ['username', 'password', 'password_confirm']

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Créer un compte')))

    class Meta:
        model = User
        exclude = ['groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'first_name', 'last_name', 'email']

    def save(self, study, *args, **kwargs):
        # Create ParticipantProfile and register participant's study
        self.instance.set_password(self.cleaned_data['password'])
        self.instance.save()
        participant_profile = ParticipantProfile()
        participant_profile.user = self.instance
        participant_profile.study = study
        participant_profile.save()
        participant_profile.populate_session_stack()
        
        user = super(SignUpForm, self).save(*args, **kwargs)
        return user

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('password_confirm')

        if User.objects.filter(username=cleaned_data['username']).exists():
            # Username exists
            self.add_error('username', _('Le nom d\'utilisateur existe déjà, veuillez choisir un autre nom d\'utilisateur'))

        if password != confirm_password:
            # Confirmation passowrd does not match
            self.add_error('password_confirm', _('Le mot de passe ne correspond pas'))

        return cleaned_data