import datetime
import json
import uuid
from datetime import timedelta as delta
from random import shuffle

import jsonfield
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelForm
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .utils import send_delayed_email
from .validators import validate_session_stack, validate_timedelta_args


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
    view_name = models.CharField(max_length=50, default='', blank=True)
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

    @property
    def unprompted(self):
        return not (bool(self.prompt) or bool(self.actions))


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
    wait = jsonfield.JSONField(default=dict, blank=True, validators=[validate_timedelta_args])  # must provide valid daytime kwargs, see https://docs.python.org/3/library/datetime.html#datetime.timedelta
    deadline = jsonfield.JSONField(default=dict, blank=True, validators=[validate_timedelta_args])  # must provide valid daytime kwargs, see https://docs.python.org/3/library/datetime.html#datetime.timedelta

    class Meta:
        ordering = ['study', 'index', 'pk']

    def __unicode__(self):
        return '.'.join([self.study.name, str(self.index), str(self.pk)])

    def __str__(self):
        return self.__unicode__()

    def clean(self, *args, **kwargs):
        '''Checks if `wait` is not greater than `deadline` if both are provided.'''
        if self.wait and self.deadline:
            if delta(**self.wait) > delta(**self.deadline):
                raise ValidationError(_(f'Cannot set wait={self.wait} and deadline={self.deadline}; wait timedelta cannot be greater than deadline timedelta.'))
        super().clean(*args, **kwargs)

    def get_task_list(self):
        '''Return a list of all tasks in BDD for this Experiment Session.'''
        return [Task.objects.get(name=task_name) for task_name in self.tasks_csv.split(',')]

    def get_task_by_index(self, index):
        '''Fetches the task instance by index in the task stack.'''
        return Task.objects.get(name=self.tasks_csv.split(',')[index])

    def get_valid_period(self, ref_timestamp, string_format=''):
        '''Returns a pair of values representing the valid period boundaries. By default, return datetime objects. If string_format is specified
        return a pair of string-formatted datetimes. If a boundary is not provided by wait or deadline, put None instead.
        '''
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
        '''Checks if session is valid at the current datetime. Specifically, we check if now is inside the valid period defined relative to
        the reference timestamp.
        '''
        now, checks = timezone.now(), []
        valid_period = self.get_valid_period(ref_timestamp)
        if valid_period[0]:
            checks.append(now > valid_period[0])
        if valid_period[1]:
            checks.append(now < valid_period[1])
        return all(checks)

    def in_future(self, ref_timestamp):
        '''Checks if session is valid at the current datetime in relation to the lower boundary of the valid period definer relative to the 
        reference timestamp.
        '''
        if not self.wait:
            return False
        now = timezone.now().replace(microsecond=0)
        if 'days' in self.wait.keys():
            start = (ref_timestamp + delta(**self.wait)).replace(microsecond=0, second=0, minute=0, hour=0)
        elif 'minutes' in self.wait.keys():
            start = ref_timestamp + delta(**self.wait)
        return now < start

    def in_past(self, ref_timestamp):
        '''Checks if session is valid at the current datetime in relation to the upper boundary of the valid period definer relative to the 
        reference timestamp.
        '''
        if not self.deadline:
            return False
        now = timezone.now().replace(microsecond=0)
        if 'days' in self.deadline.keys():
            deadline = (ref_timestamp + delta(**self.deadline)).replace(microsecond=0, second=59, minute=59, hour=23)
        elif 'minutes' in self.deadline.keys():
            deadline = ref_timestamp + delta(**self.deadline)
        return now > deadline


class ParticipantProfile(models.Model):
    # Link to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Participant preferences
    remind = models.BooleanField(default=False)
    consent = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)
    
    # Participant state
    study = models.ForeignKey(Study, null=True, on_delete=models.CASCADE)
    origin_timestamp = models.DateTimeField(default=timezone.now, verbose_name='Timestamp for when participant was first created')
    sessions = models.ManyToManyField(ExperimentSession, related_name='study_sessions')
    session_stack_csv = models.TextField(default='', null=True, blank=True, verbose_name='csv string of Session PKs', validators=[validate_session_stack])
    current_session = models.ForeignKey(ExperimentSession, null=True, blank=True, on_delete=models.DO_NOTHING)
    last_session_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Date-time of last finished session')
    task_stack_csv = models.TextField(null=True, blank=True, default='')
    extra_json = jsonfield.JSONField(default={}, blank=True)
    excluded = models.BooleanField(default=False)

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
            self.clear_session_stack(commit=True)
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
        current_session (ForeighKey) field. This is done by peeking the first element from session_stack_csv (a primary key) and
        getting the corresponding ExperimentSession that is then assigned and saved (by default). Finally, return the set session.
        If session_stack_csv is empty, return None
        '''
        if self.session_stack_csv:
            if self.current_session:
                return self.current_session
            else:
                session_stack_head = self.session_stack_peek()
                s = self.sessions.get(pk=session_stack_head)
                self.current_session = s
                self.task_stack_csv = s.tasks_csv
                if commit:
                    self.save()
                return s
        else:
            return None

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

    def session_stack_to_list(self):
        return list(self.session_stack_csv.split(','))

    def get_next_session_info(self):
        '''Return a string for when the next session starts/ends'''
        session = self.sessions.get(pk=self.session_stack_peek())
        valid_period = session.get_valid_period(self.ref_timestamp, string_format='%d %b %Y (%H:%M:%S)')
        start_info = _('commence le {}').format(valid_period[0]) if valid_period[0] else _('commence à tout moment')
        deadline_info = _('et se termine le {}').format(valid_period[1]) if valid_period[1] else _('et reste ouverte jusqu\'à ce que vous la terminiez')
        next_session_info = f'{start_info} {deadline_info}'
        return next_session_info

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
        # Clear whitespaces from task_stack_csv
        task_names = self.task_stack_csv.replace(' ','')
        if task_names:
            # If task names is not an empty string, remove possible trailing commas
            while task_names[-1] == ',': 
                task_names = task_names[:-1]
        # Finally return task name strings in a list
        return task_names.split(',')

    # Miscelaneous

    @property
    def ref_timestamp(self):
        return self.last_session_timestamp if self.last_session_timestamp else self.origin_timestamp

    @property
    def progress_info(self, all_values=False):
        l = []
        sessions = [self.sessions.get(pk=pk) for pk in self.session_stack_to_list()]
        for i, session in enumerate(sessions, 1):
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
        if self.remind and self.sessions.all() and self.session_stack_peek():
            next_session = self.sessions.get(pk=self.session_stack_peek())
            next_session_start_datetime = next_session.get_valid_period(ref_timestamp=self.ref_timestamp)[0]
            message_template = render_to_string(self.study.reminder_template,
                {'CONTEXT': {
                    'username': self.user.username,
                    'valid_period' : next_session_start_datetime,
                    'tasks': next_session.get_task_list,
                    'study_link': 'http://flowers-mot.bordeaux.inria.fr/study={}'.format(self.study.name),
                    'project_name': self.study.project,
                    'study_contact': self.study.contact
                    }
                }
            )
            index = list(ExperimentSession.objects.filter(study=self.study).values_list('pk', flat=True)).index(next_session.pk)
            send_delayed_email(
                to=self.email,
                sender=self.study.contact,
                subject='Flowers OL | Rappel de la session #{}'.format(index+1),
                message_template=message_template,
                schedule=datetime.datetime(year=next_session_start_datetime.year,
                                           month=next_session_start_datetime.month,
                                           day=next_session_start_datetime.day,
                                           hour=0)
            )
