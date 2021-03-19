from django import forms
from experiment_manager_app.models import ParticipantProfile
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML
from django.utils.translation import gettext_lazy as _


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
