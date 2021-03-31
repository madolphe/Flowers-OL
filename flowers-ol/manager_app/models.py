from random import shuffle
from django.db import models
from django.utils import timezone
import datetime, uuid, json, jsonfield
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.validators import validate_comma_separated_integer_list
from .utils import send_delayed_email
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
    """
    study = models.ForeignKey(Study, to_field='name', null=True, on_delete=models.SET_NULL)
    tasks_csv = models.CharField(max_length=200, default='')
    extra_json = jsonfield.JSONField(default=dict, blank=True)
    index = models.IntegerField(default=0)  # TODO index determines how sessions are ordered (sessions with equal indexes are randomized)
    required = models.BooleanField(default=True)
    wait = models.JSONField(default=dict, blank=True)  # must provide valid daytime kwargs, see https://docs.python.org/3/library/datetime.html#datetime.timedelta
    deadline = models.JSONField(default=dict, blank=True)  # must provide valid daytime kwargs, see https://docs.python.org/3/library/datetime.html#datetime.timedelta

    class Meta:
        ordering = ['study', 'index', 'pk']

    def __unicode__(self):
        return '.'.join([self.study.name, str(self.index), str(self.pk)])

    def __str__(self):
        return self.__unicode__()

    def get_task_list(self):
        """Return a list of all tasks in BDD for this Experiment Session"""
        return [Task.objects.get(name=task_name) for task_name in self.tasks_csv.split(',')]

    def get_task_by_index(self, index):
        return Task.objects.get(name=self.tasks_csv.split(',')[index])

    def is_today(self, ref_date):
        if self.day:
            return datetime.date.today() == ref_date + datetime.timedelta(days=self.day-1)
        return True

    def is_now(self, ref_datetime):
        if self.wait:
            return datetime.datetime.now() - ref_datetime > self.wait
        return True

    def is_past(self, ref_datetime):
        if self.day:
            return datetime.date.today() > ref_datetime + datetime.timedelta(days=self.day-1)


class ParticipantProfile(models.Model):
    # Link to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Participant preferences
    remind = models.BooleanField(default=False)
    consent = models.BooleanField(default=False)
    
    # Participant state
    study = models.ForeignKey(Study, null=True, on_delete=models.CASCADE)
    ref_dt = models.DateTimeField(default=datetime.datetime.now, verbose_name='Reference datetime')
    sessions_stack_csv = models.TextField(default='', null=True, blank=True, verbose_name='Sessions stack')
    current_session = models.ForeignKey(ExperimentSession, null=True, blank=True, on_delete=models.DO_NOTHING)
    session_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Date-time of last finished session')
    task_stack_csv = models.TextField(null=True, blank=True, default='')
    extra_json = jsonfield.JSONField(default={}, blank=True)

    class Meta:
        verbose_name = 'Participant'

    def __unicode__(self):
        return '{} -- {}'.format(self.study.name, self.user.username)

    def __str__(self):
        return self.__unicode__()

    def add_session(self, pk, commit=True):
        if self.sessions_stack_csv == '':
            self.sessions_stack_csv = str(pk)
        else:
            self.sessions_stack_csv = ','.join([self.sessions_stack_csv, str(pk)])
        if commit:
            self.save()

    def pop_session(self, commit=True):
        sessions_stack_csv = self.sessions_stack_csv
        if sessions_stack_csv:
            self.sessions_stack_csv = sessions_stack_csv.split(',')[:-1]
            if commit:
                self.save()

    def set_current_session(self):
        assert self.sessions.all(), 'Participant has no sessions assigned'
        if not self.current_session:
            s = self.sessions.first()
            self.current_session = s
            self.task_stack_csv = s.tasks_csv
            self.save()

    @property
    def current_session_valid(self):
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

    def pop_task(self, n=1):
        """Remove n items from task "stack". Return False if updated stack is empty, True otherwise"""
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

    def close_current_session(self):
        '''If sessions stack is not an empty string: 
            1. time stamp current session
            2. pop the first item
            3. clear current session
        '''
        if self.session_stack:
            self.last_session_timestamp = datetime.datetime.now()
            self.pop_session()
            self.current_session = None
            self.save()

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

    def assign_sessions(self, commit=True):
        if self.study and ExperimentSession.objects.filter(study=self.study):
            sessions = ExperimentSession.objects.filter(study=self.study)
            unique_indexes = list(set([s.index for s in sessions]))
            for i in unique_indexes:
                sessions_i = list(sessions.filter(index=i))
                if len(sessions_i) > 1:
                    shuffle(sessions_i)
                for s in sessions_i:
                    self.add_session(s.pk)
            if commit:
                self.save()
        else:
            assert False, 'No sessions found for study "{}"'.format(self.study)

    @property
    def future_sessions(self):
        if self.current_session:
            if self.sessions.exclude(pk=self.current_session.pk):
                return self.sessions.exclude(pk=self.current_session.pk)
            else:
                return []
        else:
            return self.sessions.all()

    @property
    def task_stack(self):
        return tuple([Task.objects.get(name=name) for name in self.task_names_list])

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

    @property
    def task_names_list(self):
        task_names = self.task_stack_csv.replace(' ','')
        while task_names[-1] == ',': task_names = task_names[:-1]
        task_names = task_names.split(',')
        return task_names



