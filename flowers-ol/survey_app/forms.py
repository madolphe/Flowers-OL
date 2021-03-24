from django import forms
from .widgets import get_custom_widget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div, HTML
from django.core.exceptions import *
from . import validators


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
        self.helper.add_input(Submit('submit', _('Valider')))
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
            raise ValidationError(_('Oups, il semblerait que tu as oublié de répondre à certaines questions.'))
