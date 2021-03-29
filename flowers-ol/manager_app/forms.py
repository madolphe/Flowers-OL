from django import forms
from .models import ParticipantProfile
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login


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
    username = forms.CharField(label=_('Nom d\'utilisateur'),
                               widget=forms.TextInput(attrs={'placeholder': _('Nom d\'utilisateur')}))
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

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('password_confirm')

        if password != confirm_password:
            self.add_error('password_confirm', _('Le mot de passe ne correspond pas'))

        return cleaned_data


class ConsentForm(forms.Form):
    """
    Class to generate a form for consent page.
    """
    understood = forms.BooleanField(label="J'ai lu et compris les termes de cette étude")
    agreed = forms.CharField(label='Consentement', help_text='Ecrire \"Je consens\" dans la barre')
    fields = ['understood', 'agreed']

    def __init__(self, *args, **kwargs):
        super(ConsentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Valider'))

    def clean_agreed(self):
        user_input = self.cleaned_data['agreed'].lower().strip('\"')
        if user_input != 'je consens':
            raise forms.ValidationError('Veuillez donner votre consentement en écrivant "Je consens" '
                                        'pour valider votre participation')
        return user_input
