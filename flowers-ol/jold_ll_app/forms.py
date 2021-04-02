from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML
from django.utils.translation import gettext as _


class ConsentForm(forms.Form):
    understood = forms.BooleanField(label=_("J'ai lu et compris les termes de cette étude"), required=True)
    agreed = forms.BooleanField(label=_("I understand that by checking this box I provide my informed consent to participate in the study"), required=True)
    request_reminder = forms.BooleanField(label=_('I would like to be reminded about further sessions 1 day before'), required=False)
    email = forms.EmailField(required=False)
    fields = ['understood', 'agreed']

    def __init__(self, *args, **kwargs):
        super(ConsentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Valider')))
