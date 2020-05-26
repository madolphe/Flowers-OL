from django import forms
from .models import ParticipantProfile, QBank
from .widgets import rangeLikert
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.shortcuts import render, redirect, HttpResponse



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
                   'wind', 'dist', 'plat', 'nb_followups_finished']
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


class JOLDPostSessForm(forms.Form):
    def __init__(self, questions, index, *args, **kwargs):
        super(JOLDPostSessForm, self).__init__(*args, **kwargs)
        self.rows = []
        self.index = index
        for i, q in enumerate(questions, 1):
            if q.widget == 'range' or q.widget == 'likert':
                self.fields[q.handle] = forms.IntegerField(
                    widget = rangeLikert(attrs={'annotations': q.annotations.split('~'),
                                                'min_': q.min_val,
                                                'max_': q.max_val,
                                                'step': q.step}),
                    label = '{}. {}'.format(i, q.prompt))
                self.fields[q.handle+'_validator'] = forms.BooleanField(label = '')
                self.rows.append(
                    Row(Column(q.handle, css_class='form-group col-10'),
                        Column(q.handle+'_validator', css_class='form-group col-2')))
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(*self.rows)
