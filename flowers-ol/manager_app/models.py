from random import shuffle
from django.db import models
from django.utils import timezone
import datetime, uuid, json, jsonfield
from datetime import timedelta as delta
from django.contrib.auth.models import User
from django.forms import ModelForm
from .utils import send_delayed_email
from .validators import validate_session_stack, validate_timedelta_args
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


class Study(models.Model):
    name = models.CharField(max_length=50, default=uuid.uuid4, unique=True)
    project = models.CharField(max_length=100, default='')
    base_template = models.CharField(max_length=50, default='base.html')
    style = models.CharField(default='css/home.css', max_length=50, null=True)
    briefing_template = models.CharField(max_length=50, null=True, blank=True)
    reminder_template = models.CharField(max_length=50, null=True, blank=True)
    extra_json = jsonfield.JSONField(default={}, blank=True)
    contact = models.EmailField(default='')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    class Meta:
        verbose_name = 'Study'
        verbose_name_plural = 'Studies'


class Task(models.Model):
    name = models.CharField(max_length=50, default='', unique=True)
    description = models.TextField(default='', blank=True)
    prompt = models.CharField(max_length=100, default='', blank=True)
    view_name = models.CharField(max_length=50, default='')
    exit_view = models.CharField(max_length=50, default='', blank=True)
    info_templates_csv = models.TextField(null=True, blank=True)
    extra_json = jsonfield.JSONField(default={}, blank=True)
    actions = jsonfield.JSONField(default={}, blank=True)  # Must be a csv of valid views

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    @property
    def info(self):
        l, hidden = [], False
        for i in self.info_templates_csv.split(','):
            label, template = i.split('=')
            if template[-1]=='-':
                template = template[:-1]
                hidden = True
            l.append((label, template, hidden))
        return l


class ExperimentSession(models.Model):
    """
    Model that represent a particular experiment for a participant.
    Note: `timedeltas_validated` is a hacky way to ensure we run our custom field and model validators 
    when an instance of ExperimentSession is used to determine that the session is valid at a given time
    """
    study = models.ForeignKey(Study, to_field='name', null=True, on_delete=models.SET_NULL)
    tasks_csv = models.CharField(max_length=200, default='')
    extra_json = jsonfield.JSONField(default=dict, blank=True)
    index = models.IntegerField(default=0)  # TODO index determines how sessions are ordered (sessions with equal indexes are randomized)
    required = models.BooleanField(default=True)
    wait = models.JSONField(default=dict, blank=True, validators=[validate_timedelta_args])  # must provide valid daytime kwargs, see https://docs.python.org/3/library/datetime.html#datetime.timedelta
    deadline = models.JSONField(default=dict, blank=True, validators=[validate_timedelta_args])  # must provide valid daytime kwargs, see https://docs.python.org/3/library/datetime.html#datetime.timedelta

    class Meta:
        ordering = ['study', 'index', 'pk']

    def __unicode__(self):
        return '.'.join([self.study.name, str(self.index), str(self.pk)])

    def __str__(self):
        return self.__unicode__()

    def clean(self, *args, **kwargs):
        '''Checks if `wait` is not greater than `deadline` if both are provided'''
        if self.wait and self.deadline:
            if delta(**self.wait) > delta(**self.deadline):
                raise ValidationError(_(f'Cannot set wait={self.wait} and deadline={self.deadline}; wait timedelta cannot be greater than deadline timedelta.'))
        super().clean(*args, **kwargs)

    def get_task_list(self):
        """Return a list of all tasks in BDD for this Experiment Session"""
        return [Task.objects.get(name=task_name) for task_name in self.tasks_csv.split(',')]

    def get_task_by_index(self, index):
        return Task.objects.get(name=self.tasks_csv.split(',')[index])

    def get_valid_period(self, ref_timestamp, string_format=''):
        valid_period = [None, None]
        for i, constraint in enumerate([self.wait, self.deadline]):
            if 'days' in constraint.keys():
                valid_period[i] = (ref_timestamp + delta(**constraint)).replace(microsecond=0, second=59*i, minute=59*i, hour=23*i)
            elif 'minutes' in constraint.keys():
                valid_period[i] = ref_timestamp + delta(**constraint)
        if string_format:
            return [t.strftime(string_format) if t else None for t in valid_period]
        return valid_period

    def is_valid_now(self, ref_timestamp):
        now, checks = timezone.now(), []
        valid_period = self.get_valid_period(ref_timestamp)
        if valid_period[0]:
            checks.append(now > valid_period[0])
        if valid_period[1]:
            checks.append(now < valid_period[1])
        return all(checks)


class ParticipantProfile(models.Model):
    # Link to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Participant preferences
    remind = models.BooleanField(default=False)
    consent = models.BooleanField(default=False)
    
    # Participant state
    study = models.ForeignKey(Study, null=True, on_delete=models.CASCADE)
    origin_timestamp = models.DateTimeField(default=timezone.now, verbose_name='Timestamp for when participant was first created')
    sessions = models.ManyToManyField(ExperimentSession, related_name='study_sessions')
    session_stack_csv = models.TextField(default='', null=True, blank=True, verbose_name='csv string of Session PKs', validators=[validate_session_stack])
    current_session = models.ForeignKey(ExperimentSession, null=True, blank=True, on_delete=models.DO_NOTHING)
    last_session_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Date-time of last finished session')
    task_stack_csv = models.TextField(null=True, blank=True, default='')
    extra_json = jsonfield.JSONField(default={}, blank=True)

    class Meta:
        verbose_name = 'Participant'

    def __unicode__(self):
        return '{} -- {}'.format(self.study.name, self.user.username)

    def __str__(self):
        return self.__unicode__()

    # Session management

    def session_stack_peek(self, index=0):
        '''Returns the indexed value from the session_stack_csv'''
        return self.session_stack_csv.split(',')[index]

    def session_stack_append(self, pk, commit=True):
        '''Adds an ExperimentSession primary key to session_stack_csv'''
        if self.session_stack_csv == '':
            self.session_stack_csv = str(pk)
        else:
            self.session_stack_csv = ','.join([self.session_stack_csv, str(pk)])
        if commit:
            self.save()

    def session_stack_pop(self, commit=True):
        '''Removes the first primary key of an ExperimentSession from the session_stack_csv of primary keys if the stack is not empty'''
        stack_copy = self.session_stack_csv.split(',')
        if stack_copy:
            pk = stack_copy.pop(0)
            self.session_stack_csv = ','.join(stack_copy)
            if commit:
                self.save()
        return pk
    
    def clear_session_stack(self, commit=True):
        '''Clears session_stack_csv turning it into an empty list'''
        session_stack = self.session_stack_csv
        if session_stack:
            self.session_stack_csv = ''
            if commit:
                self.save()

    def populate_session_stack(self, commit=True):
        ''' Queries ExperimentSessions associated with participant's study, orders them by index, and
        populates participants session_tack_csv with pk's of ordered sessions (order of equal indexes
        is determined randomly)
        '''
        if self.study and ExperimentSession.objects.filter(study=self.study):
            self.reset_session_stack(commit=True)
            sessions = ExperimentSession.objects.filter(study=self.study)
            self.sessions.add(*sessions)
            unique_indexes = list(set([s.index for s in sessions]))
            for i in unique_indexes:
                sessions_i = list(sessions.filter(index=i))
                if len(sessions_i) > 1:
                    shuffle(sessions_i)
                for s in sessions_i:
                    self.session_stack_append(s.pk)
            if commit:
                self.clean_fields()
                self.save()
        else:
            assert False, 'No sessions found for study "{}"'.format(self.study)

    def set_current_session(self, commit=True):
        '''If session_stack_csv is not empty, set_current_session() assigns an ExperimentSession instance to the participant's
        current_session (ForeighKey) field. This is done by getting the first element (a primary key) from session_stack_csv and
        querying a corresponding ExperimentSession that is then assigned and saved (by default)
        '''
        assert self.session_stack_csv, 'Session "stack" is an empty string. Did you forget to assign sessions and create a sessions stack?'
        if not self.current_session:
            session_stack_head = self.session_stack_peek()
            s = self.sessions.get(pk=session_stack_head)
            self.current_session = s
            self.task_stack_csv = s.tasks_csv
            if commit:
                self.save()

    def close_current_session(self, commit=True):
        '''If sessions stack is not an empty string: 
            1. time stamp current session
            2. pop the first item
            3. clear current session
        '''
        if self.session_stack_csv:
            self.last_session_timestamp = timezone.now().replace(microsecond=0)
            self.session_stack_pop()
            self.current_session = None
            if commit:
                self.save()

    @property
    def future_sessions(self):
        if self.current_session:
            if self.sessions.exclude(pk=self.current_session.pk):
                return self.sessions.exclude(pk=self.current_session.pk)
            else:
                return []
        else:
            return self.sessions.all()

    def old_validator(self):
        # If the current session is not today, not required and was skipped (i.e date in the past):
        if not self.current_session.is_today(ref_date=self.ref_dt.date()):
            if not self.current_session.required and self.current_session.is_past(ref_datetime=self.ref_dt.date()):
                # Store in participant extra_json when a session has been skipped:
                if 'skipped_session' in self.extra_json:
                    self.extra_json['skipped_session'].append((self.current_session.day, self.current_session.index))
                else:
                    self.extra_json['skipped_session'] = [(self.current_session.day, self.current_session.index)]
                if 'game_time_to_end' in self.extra_json:
                    del self.extra_json['game_time_to_end']
                self.close_current_session()
                self.set_current_session()
                return self.current_session_valid
            return False
        if self.session_timestamp and not self.current_session.is_now(ref_datetime=self.session_timestamp):
            return False
        return True

    # Task management

    def pop_task(self, n=1):
        '''Remove n items from task "stack". Return False if updated stack is empty, True otherwise'''
        task_names = self.task_stack_csv.split(',')[n:]
        self.task_stack_csv = ','.join(task_names)
        self.save()
        print(self.task_stack_csv)

    @property
    def current_task(self):
        if not self.task_stack_csv:
            return None
        stack_head = self.task_stack_csv.split(',')[0]
        return Task.objects.get(name=stack_head)

    @property
    def task_stack(self):
        return tuple([Task.objects.get(name=name) for name in self.task_names_list])

    @property
    def task_names_list(self):
        task_names = self.task_stack_csv.replace(' ','')
        while task_names[-1] == ',': task_names = task_names[:-1]
        task_names = task_names.split(',')
        return task_names

    # Miscelaneous

    @property
    def progress_info(self, all_values=False):
        l = []
        for i, session in enumerate(ExperimentSession.objects.filter(study=self.study), 1):
            tasks = [task.description for task in session.get_task_list()]
            task_index = None
            if session == self.current_session:
                task_index = len(tasks) - len(self.task_names_list)
                # From this session, append other sess:
                all_values = True
            if all_values:
                sess_info = {'num': i,
                             'current': True if session == self.current_session else False,
                             'tasks': tasks,
                             'cti': task_index} # cti = current task index
                l.append(sess_info)
        return l

    def queue_reminder(self):
        if self.remind and self.sessions.all():
            day1 = self.ref_dt
            next_session = self.sessions.first()
            next_session_date = day1 + datetime.timedelta(days=next_session.day-1)
            message_template = render_to_string(self.study.reminder_template,
                {'CONTEXT': {
                    'name': self.user.first_name.lower().capitalize(),
                    'session_date' : next_session_date.date().strftime('%d-%m-%Y'),
                    'tasks': next_session.get_task_list,
                    'study_link': 'http://flowers-mot.bordeaux.inria.fr/study={}'.format(self.study.name),
                    'project_name': self.study.project,
                    'study_contact': self.study.contact
                    }
                }
            )
            index = list(ExperimentSession.objects.filter(study=self.study).values_list('pk', flat=True)).index(next_session.pk)
            send_delayed_email(
                to=self.user.email,
                sender=self.study.contact,
                subject='Flowers OL | Rappel de la session #{}'.format(index+1),
                message_template=message_template,
                schedule=datetime.datetime(year=next_session_date.year,
                                           month=next_session_date.month,
                                           day=next_session_date.day,
                                           hour=6)
            )
