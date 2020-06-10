from django import forms
from .models import ParticipantProfile, QBank
from .widgets import get_custom_Likert_widget
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div
from django.core.exceptions import *

# @TODO: add to condition ==> connect to ZPDES/baseline
    # @TODO: install kidlib
    # @TODO: install connect and see what has to be saved
# @TODO: add NASA TLX (french version)


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
                   'wind', 'dist', 'plat', 'nb_followups_finished', 'consent', 'sexe', 'job'
                   , 'video_game_start', 'game_habit', 'driver', 'driving_start', 'attention_training'
                   , 'online_training', 'video_game_habit', 'video_game_freq', 'driving_freq', 'general_profil',
                   'attention_profil', 'condition']
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
    # understood = forms.BooleanField(label='I have read and understood the terms of participation')
    understood = forms.BooleanField(label='J\'ai lu et compris les termes de la participation')
    # agreed = forms.CharField(label='Informed consent', help_text='Type \"I consent\" into the box')
    agreed = forms.CharField(label='Informez le consentement', help_text='Écrire, \"Je consens\" dans l\'espace dédié')
    fields = ['understood', 'agreed']

    def __init__(self, *args, **kwargs):
        super(ConsentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean_agreed(self):
        user_input = self.cleaned_data['agreed'].lower().strip('\"')
        print(user_input)
        # if user_input != 'i consent':
        #    raise forms.ValidationError('Please provide your explicit informed consent by typing "I consent"')
        if user_input != 'je consens':
            raise forms.ValidationError('S\'il vous plaît, exprimez votre consentement en écrivant "Je consens"')
        return user_input


def validate_checked(value):
    if not value:
        print('No value')
        raise ValidationError(
            ('%(value)s'),
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
        print(cleaned_data)
        missing_data = False
        for handle in sorted(list(self.fields.keys())):
            if not cleaned_data.get(handle):
                self.helper[handle].wrap(Div, css_class='empty-row')
                missing_data = True
            else:
                self.fields[handle].widget.attrs['checked'] = cleaned_data[handle]
        if missing_data:
            raise forms.ValidationError('Oops, looks like you have missed some fields.')


class ZPDESGetProfilForm(forms.ModelForm):

    def __init__(self, questions, *args, **kwargs):
        super(ZPDESGetProfilForm, self).__init__(*args, **kwargs)
        self.choice_questions = questions
        self.rows = []
        self.names = {}
        for key, value in enumerate(questions, 1):
            self.names[value.handle] = key - 1
            # Check what kind of field (either integer if range or charfield if categories)
            if value.handle == 'video_game_habit':
                self.fields[value.handle] = forms.CharField(label='', validators=[validate_checked])
            else:
                self.fields[value.handle] = forms.IntegerField(label='',
                                                               validators=[validate_checked])
            self.fields[value.handle].widget = get_custom_Likert_widget(value)
            if self.fields[value.handle].widget.needs_validator:
                self.fields[value.handle+'_validator'] = forms.BooleanField(label='')
                self.rows.append(
                    Row(Column(value.handle, css_class='form-group col-11'),
                        Column(value.handle+'_validator', css_class='form-group col-1'))
                )
                # Set validator value to absurd value
                self.names[value.handle+'_validator'] = -1
            else:
                self.rows.append(
                    Row(Column(value.handle, css_class='form-group col-12'), css_class='likert-form-row'))
        # Build layout according to self.fields:
        self.layout = []
        for obj in self.fields:
            if obj in self.names:
                # if this is not a validator object:
                if self.names[obj] != -1:
                    self.layout.append(self.rows[self.names[obj]])
            else:
                self.layout.append(Row(Column(obj, css_class='form-group col-12')))
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_tag = False
        self.helper.add_layout(Layout(*self.layout))

    class Meta:
        model = ParticipantProfile
        fields = ['sexe', 'screen_params', 'job', 'video_game_start', 'video_game_freq', 'driver', 'driving_start',
                  'driving_freq', 'attention_training', 'online_training', 'video_game_habit']
        labels = {'screen_params': 'Diagonale de l\'écran (en cm)', 'sexe': 'Genre', 'job': 'Activité professionnelle',
                  'video_game_start': 'Début de la pratique des jeux vidéos',
                  'game_habit': 'Quels types de jeu pratiquez vous ?',
                  'driver': 'Permis de conduire', 'driving_start': 'Depuis combien d\'années conduisez-vous?',
                  'attention_training': 'Avez-vous déjà suivi un protocole d\'entraînement de l\'attention?',
                  'online_training': 'Avez-vous déjà suivi des formations en ligne? '}
        help_texts = {'screen_params': 'Cette information peut être récupérée dans les paramètres d\'écran.'}

    def clean_video_game_habit(self):
        game_habit = ['FPS', 'Action', 'Sport', 'MMO', 'RPG']
        return [game_habit[int(elt)] for elt in self.data.getlist('video_game_habit')]

    def clean(self):
        cleaned_data = super().clean()
        missing_data = False
        for handle in sorted(list(self.fields.keys())):
            if handle not in cleaned_data:
                self.helper[handle].wrap(Div, css_class='empty-row')
                missing_data = True
            else:
                self.fields[handle].widget.attrs['checked'] = cleaned_data[handle]
        if missing_data:
            raise forms.ValidationError('Oops, veuillez compléter tous les champs s\'il vous plaît.')
