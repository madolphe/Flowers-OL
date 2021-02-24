from django import forms
from .models import ParticipantProfile
from .widgets import get_custom_widget
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML
from django.core.exceptions import *
from django.forms.widgets import NumberInput, CheckboxInput
from . import validators
import datetime
from django.utils.translation import gettext_lazy as _


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


class QuestionnaireForm(forms.Form):
    """
    Generic questionnaire form.
    """
    def __init__(self, questions, *args, **kwargs):
        # Pass questions as an attribute to use it in clean method
        self.questions = questions
        super(QuestionnaireForm, self).__init__(*args, **kwargs)
        validator_ = False
        self.rows = []
        # Build a row for each question:
        for i, q in enumerate(questions, 1):
            # Get all validators that match `vname` or get None if name does not match. Then filter out `None`s
            validators_list = [getattr(validators, vname, None) for vname in q.validate.split(',')]
            # Create a default charfield without label
            self.fields[q.handle] = forms.CharField(label='', validators=[v for v in validators_list if v])
            # Add help_text
            self.fields[q.handle].help_text = q.help_text
            # Add correct widget (possibly a custom one)
            self.fields[q.handle].widget = get_custom_widget(q, num=i)
            # Build the div object:
            question_widget = [Div(q.handle)]
            if hasattr(self.fields[q.handle].widget, "needs_validator") and self.fields[q.handle].widget.needs_validator:
                self.fields[q.handle+'_validator'] = forms.BooleanField(label='')
                question_widget.append(Div(q.handle+'_validator', css_class='question-validator'))
            row_list = [
                HTML('<div class="question-prompt">{}. {}</div>'.format(i, q.prompt)),
                Div(*question_widget, css_class='question-widget')
            ]
            self.rows.append(Row(*row_list, css_class='custom-form-row {}'.format(' odd' if i % 2 else '')))
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Valider'))
        self.helper.layout = Layout(*self.rows)
        self.helper.form_show_errors = True

    def clean(self):
        """
        Method called when a form is sent. Add a warning when a row is empty.
        """
        cleaned_data = super().clean()
        missing_data = False
        for handle in sorted(list(self.fields.keys())):
            # print('{}: value = {}'.format(handle, cleaned_data.get(handle)))
            # if a particular field is empty:
            if cleaned_data.get(handle) is None:
                self.helper[handle].wrap(Div, css_class='empty-row')
                missing_data = True
            else:
                self.fields[handle].widget.attrs['prev'] = cleaned_data[handle]
        if missing_data:
            raise ValidationError('Oups, il semblerait que tu as oublié de répondre à certaines questions.')
