from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML


class ConsentForm(forms.Form):
    understood = forms.BooleanField(label=_("En cochant cette case, vous reconnaissez avoir lu et compris les informations fournies sur l'étude."), required=True)
    agreed = forms.BooleanField(label=_("En cochant cette case, vous donnez votre consentement éclairé à participer à l'étude."), required=True)
    request_reminder = forms.BooleanField(label=_('En cochant cette case, vous acceptez de recevoir un rappel 1 jour avant la prochaine session (optionel).'), required=False)
    email = forms.EmailField(label=_('À quelle adresse souhaitez-vous recevoir le(s) rappel(s) ? Indiquez votre adresse électronique ci-dessous (optionel)'), required=False)
    fields = ['understood', 'agreed']

    def __init__(self, *args, **kwargs):
        super(ConsentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Soumettre le consentement éclairé')))
