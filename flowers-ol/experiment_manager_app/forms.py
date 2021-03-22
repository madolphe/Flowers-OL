from django import forms
from .models import ParticipantProfile
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login


class UserForm(forms.ModelForm):
    """
    Class to generate user form : [CreateUserForm already exists and could be overwritten]
    """
    username = forms.CharField(label=_("Nom d'utilisateur"),
                               widget=forms.TextInput(attrs={'placeholder': _("Nom d'utilisateur")}))
    password = forms.CharField(label=_('Mot de passe'),
                               widget=forms.PasswordInput(attrs={'placeholder': _('Mot de passe')}))
    first_name = forms.CharField(label='Prénom', widget=forms.TextInput(attrs={'placeholder': 'Prénom'}))
    last_name = forms.CharField(label='Nom de famille', widget=forms.TextInput(attrs={'placeholder': 'Nom de famille'}))
    email = forms.CharField(label='E-mail', widget=forms.TextInput(attrs={'placeholder': 'E-mail'}))
    field_order = ['username', 'password', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = User
        exclude = ['groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined']


class ParticipantProfileForm(forms.ModelForm):
    """
    Class to generate a form used to register a participant.
    """
    def __init__(self, *args, **kwargs):
        super(ParticipantProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Valider'))
        self.helper.form_tag = False
        self.fields['birth_date'].label = _('Date de naissance')
        self.fields['remind'].label = _('Rappelez-moi par e-mail de compléter les tâches pour l\'étude')

    class Meta:
        model = ParticipantProfile
        fields = ['birth_date', 'study', 'remind']
        widgets = {'study': forms.HiddenInput(),
                   'birth_date': forms.DateInput(attrs={'type': 'date'})
                   }

    def save_profile(self, user):
        """
        Method to link participant profile and django user
        :param user:
        :return:
        """
        participant_profile = super().save(commit=False)
        participant_profile.user = user
        super().save(commit=True)


class SignInForm(forms.Form):
    """
    Class to generate a form for logging page.
    """
    username = forms.CharField(label=_("Nom d'utilisateur"),
                               widget=forms.TextInput(attrs={'placeholder': _("Nom d'utilisateur")}))
    password = forms.CharField(label="Mot de passe",
                               widget=forms.PasswordInput(attrs={'placeholder': _('Mot de passe')}))
    fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Se connecter'))


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


################# MANAGE DIFFERENT FORMS FOR DIFFERENT STUDIES #######################

from mot_app.forms import ProlificUserForm, ProlificParticipantProfileForm


def get_default_forms(request, study):
    form_user = UserForm(request.POST or None)
    form_profile = ParticipantProfileForm(request.POST or None, initial={'study': study})
    return {"form_user": form_user, "form_profile": form_profile}


def default_store_infos(request, forms):
    # Get extra-info for user profile:
    user = forms['form_user'].save(commit=False)
    # Use set_password in order to hash password
    user.set_password(forms['form_user'].cleaned_data['password'])
    user.save()
    forms['form_profile'].save_profile(user)
    login(request, user)


def get_ubx_forms(request, study):
    form_user = UserForm(request.POST or None)
    form_profile = ParticipantProfileForm(request.POST or None, initial={'study': study})


def get_prolific_forms(request, study):
    return {
        "form_user": ProlificUserForm(request.POST or None),
        "form_profile": ProlificParticipantProfileForm(request.POST or None, initial={'study': study})
    }


def prolific_store_infos(request, forms):
    # Get extra-info for user profile:
    user = forms['form_user'].save(commit=False)
    # Use set_password in order to hash password
    user.set_password(forms['form_user'].cleaned_data['password'])
    user.save()
    forms['form_profile'].save_profile(user)
    login(request, user)


def ubx_store_infos(request, forms):
    # Get extra-info for user profile:
    user = forms['form_user'].save(commit=False)
    # Use set_password in order to hash password
    user.set_password(forms['form_user'].cleaned_data['password'])
    user.save()
    forms['form_profile'].save_profile(user)
    login(request, user)


FORMS = {
    'default': (get_default_forms, default_store_infos),
    'v0_ubx': (get_default_forms, default_store_infos),
    'v0_prolific': (get_prolific_forms, prolific_store_infos)
}

