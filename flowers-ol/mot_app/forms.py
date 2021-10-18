from django import forms
from manager_app.models import ParticipantProfile
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML
from django.utils.translation import gettext_lazy as _


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
    fields = ['understood', 'agreed', 'email', 'request_reminder']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        is_prolific_user = kwargs.pop('is_prolific_user', False)
        super(ConsentForm, self).__init__(*args, **kwargs)
        if is_prolific_user:
            del self.fields['email']
            del self.fields['request_reminder']
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Soumettre le consentement éclairé')))

    def clean(self):
        cleaned_data = super(ConsentForm, self).clean()
        error = False
        if 'email' and 'request_reminder' in self.fields:
            if cleaned_data['request_reminder'] and not cleaned_data['email']:
                self.add_error('email', _('Veuillez fournir une adresse électronique si vous souhaitez recevoir un '
                                          'rappel de la future session 1 jour à l\'avance.'))

            if not cleaned_data['request_reminder'] and cleaned_data['email']:
                self.add_error('request_reminder', _('Si vous souhaitez recevoir un rappel par courriel au sujet de la '
                                                     'prochaine session, veuillez cocher cette case. Si vous ne '
                                                     'souhaitez pas recevoir de tels rappels, décochez cette case et '
                                                     'supprimez votre courriel ci-dessous.'))
        return cleaned_data
