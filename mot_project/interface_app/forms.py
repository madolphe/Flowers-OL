from django import forms
from .models import ParticipantProfile, QBank
from .widgets import get_custom_Likert_widget
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field


class UserForm(forms.ModelForm):
    """
    Class to generate user form : !!! CreateUserForm already exists and could be override !!!
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'first name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'last name'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'email'}))

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        pass

    class Meta:
        model = User
        exclude = ['groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined']


class ParticipantProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ParticipantProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_tag = False
        pass

    class Meta:
        model = ParticipantProfile
        exclude = ['user', 'date', 'screen_params', 'nb_sess_started', 'nb_sess_finished',
                   'wind', 'dist', 'plat', 'nb_followups_finished', 'consent']
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
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
    fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))


class ConsentForm(forms.Form):
    understood = forms.BooleanField(label='I have read and understood the terms of participation')
    agreed = forms.CharField(label='Informed consent', help_text='Type \"I consent\" into the box')
    fields = ['understood', 'agreed']

    def __init__(self, *args, **kwargs):
        super(ConsentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean_agreed(self):
        user_input = self.cleaned_data['agreed'].lower().strip('\"')
        if user_input != 'i consent':
            raise forms.ValidationError('Please provide your explicit informed consent by typing "I consent"')
        return user_input


def validate_checked(value):
    if not value:
        print('No value')
        raise ValidationError(
            _('%(value)s'),
            params={'value': value},
        )


class JOLDPostSessForm(forms.Form):
    def __init__(self, questions, index, *args, **kwargs):
        super(JOLDPostSessForm, self).__init__(*args, **kwargs)
        validator_ = False
        self.rows = []
        self.index = index
        for i, q in enumerate(questions, 1):
            self.fields[q.handle] = forms.IntegerField(
                label = '',
                validators = [validate_checked])
            self.fields[q.handle].widget = get_custom_Likert_widget(q, index=i)
            if self.fields[q.handle].widget.needs_validator:
                self.fields[q.handle+'_validator'] = forms.BooleanField(label='')
                self.rows.append(
                    Row(Column(q.handle, css_class='form-group col-11'),
                        Column(q.handle+'_validator', css_class='form-group col-1'))
                )
            else:
                self.rows.append(
                    Row(Column(q.handle, css_class='form-group col-12'), css_class='likert-form-row'))
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(*self.rows)

    def clean(self):
        cleaned_data = super().clean()
        missing_data = False
        for handle in sorted(list(self.fields.keys())):
            if not cleaned_data.get(handle):
                self.helper[handle].wrap(Div, css_class='empty-row')
                missing_data = True
            else:
                self.fields[handle].widget.attrs['checked'] = cleaned_data[handle]
        if missing_data:
            raise forms.ValidationError('Oops, looks like you have missed some fields.')
