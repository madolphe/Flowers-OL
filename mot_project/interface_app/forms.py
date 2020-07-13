from django import forms
from .models import ParticipantProfile
from .widgets import get_custom_widget
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML
from django.core.exceptions import *
from django.forms.widgets import NumberInput, CheckboxInput

# @TODO: add to condition ==> connect to ZPDES/baseline
    # @TODO: install kidlib
    # @TODO: install connect and see what has to be saved


class UserForm(forms.ModelForm):
    """
    Class to generate user form : !!! CreateUserForm already exists and could be override !!!
    """
    username = forms.CharField(label="Nom d'utilisateur", widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"}))
    password = forms.CharField(label= 'Mot de passe', widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}))
    first_name = forms.CharField(label='Prénom', widget=forms.TextInput(attrs={'placeholder': 'Prénom'}))
    last_name = forms.CharField(label='Nom de famille', widget=forms.TextInput(attrs={'placeholder': 'Nom de famille'}))
    email = forms.CharField(label='E-mail', widget=forms.TextInput(attrs={'placeholder': 'E-mail'}))

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        pass

    class Meta:
        model = User
        exclude = ['groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined']
    field_order = ['username', 'password', 'first_name', 'last_name', 'email']


class ParticipantProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ParticipantProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Valider'))
        self.helper.form_tag = False
        self.fields['birth_date'].label = 'Date de naissance'
        self.fields['remind'].label = 'Rappelez-moi par e-mail de compléter les tâches pour l\'étude'

    class Meta:
        model = ParticipantProfile
        fields = ['birth_date', 'study', 'remind']
        widgets = {'study': forms.HiddenInput()}

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
    username = forms.CharField(label="Nom d'utilisateur", widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}))
    fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Se connecter'))


class ConsentForm(forms.Form):
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
            raise forms.ValidationError('Veuillez donner votre consentement en écrivant "Je consens" pour valider votre participation')
        return user_input


def validate_checked(value):
    if not value:
        print('No value')
        raise ValidationError(
            ('%(value)s'),
            params={'value': value},
        )


class JOLDQuestionBlockForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        # Pass questions as an attribute to use it in clean method
        self.questions = questions
        super(JOLDQuestionBlockForm, self).__init__(*args, **kwargs)
        validator_ = False
        self.rows = []
        for i, q in enumerate(questions, 1):
            self.fields[q.handle] = forms.CharField(label='', validators=[validate_checked])
            self.fields[q.handle].help_text = q.help_text
            self.fields[q.handle].widget = get_custom_widget(q, num=i)
            question_widget = [Div(q.handle)]
            if hasattr(self.fields[q.handle].widget, "needs_validator") and self.fields[q.handle].widget.needs_validator:
                self.fields[q.handle+'_validator'] = forms.BooleanField(label='')
                question_widget.append(Div(q.handle+'_validator', css_class='question-validator'))
            row_list = [
                HTML('<div class="question-prompt">{}. {}</div>'.format(i, q.prompt)),
                Div(*question_widget, css_class='question-widget')
            ]

            self.rows.append(Row(*row_list, css_class='custom-form-row {}'.format(' odd' if i%2 else '')))
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Valider'))
        self.helper.layout = Layout(*self.rows)

    def clean(self):
        cleaned_data = super().clean()
        missing_data = False
        for handle in sorted(list(self.fields.keys())):
            print('{}: {}'.format(handle, cleaned_data.get(handle)))
            if cleaned_data.get(handle) is None:
                self.helper[handle].wrap(Div, css_class='empty-row')
                missing_data = True
            else:
                self.fields[handle].widget.attrs['prev'] = cleaned_data[handle]
        if missing_data:
            raise forms.ValidationError('Oups, il semblerait que tu as oublié de répondre à certaines questions.')
