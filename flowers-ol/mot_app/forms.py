from django import forms
from manager_app.models import ParticipantProfile
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML
from django.utils.translation import gettext_lazy as _
from django.contrib import messages as django_messages


class ProlificUserForm(forms.ModelForm):
    """
    Class to generate user form : [CreateUserForm already exists and could be overwritten]
    """
    username = forms.CharField(label=_("Prolific_ID"),
                               widget=forms.TextInput(attrs={'placeholder': _("Prolific ID")}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(attrs={'placeholder': _("Password")}))
    field_order = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(ProlificUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = User
        exclude = ['groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined']
        fields = ['username', 'password']


class ProlificParticipantProfileForm(forms.ModelForm):
    """
    Class to generate a form used to register a participant.
    """
    def __init__(self, *args, **kwargs):
        super(ProlificParticipantProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Valider'))
        self.helper.form_tag = False
        self.fields['remind'].label = _('Remind my when a task is available with my Prolific account.')

    class Meta:
        model = ParticipantProfile
        fields = ['study', 'remind']
        widgets = {'study': forms.HiddenInput()}
        exclude = ['name']

    def save_profile(self, user):
        """
        Method to link participant profile and django user
        :param user:
        :return:
        """
        participant_profile = super().save(commit=False)
        participant_profile.user = user
        super().save(commit=True)


class ConsentForm(forms.Form):
    understood = forms.BooleanField(
        label=_("En cochant cette case, vous reconnaissez avoir lu et compris les informations fournies sur l'étude."),
        required=True)
    agreed = forms.BooleanField(
        label=_("En cochant cette case, vous donnez votre consentement éclairé à participer à l'étude."), required=True)
    request_reminder = forms.BooleanField(label=_(
        'En cochant cette case, vous acceptez de recevoir un rappel 1 jour avant la prochaine session (optionnel).'),
                                          required=False)
    email = forms.EmailField(label=_(
        'Adresse électronique si vous souhaitez recevoir des rappels (non obligatoire):'),
                            required=False,
                            widget=forms.EmailInput(attrs={'placeholder': 'adresse@mail.com'})
    )
    fields = ['understood', 'agreed']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ConsentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Soumettre le consentement éclairé')))

    def clean(self):
        cleaned_data = super(ConsentForm, self).clean()
        error = False

        if cleaned_data['request_reminder'] and not cleaned_data['email']:
            self.add_error('email', _(
                'Veuillez fournir une adresse électronique si vous souhaitez recevoir un rappel de la future session 1 jour à l\'avance.'))

        if not cleaned_data['request_reminder'] and cleaned_data['email']:
            self.add_error('request_reminder', _(
                'Si vous souhaitez recevoir un rappel par courriel au sujet de la prochaine session, veuillez cocher cette case. Si vous ne souhaitez pas recevoir de tels rappels, décochez cette case et supprimez votre courriel ci-dessous.'))
        return cleaned_data