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
    day = models.IntegerField(default=0) # have to use default=0 because nulls are not compared for uniqueness
    index = models.IntegerField(default=0)
    wait = models.DurationField(default=datetime.timedelta(0))
    required = models.BooleanField(default=True)
    tasks_csv = models.CharField(max_length=200, default='')
    extra_json = jsonfield.JSONField(default={}, blank=True)

    class Meta:
        ordering = ['study', 'day', 'index']
        unique_together = ['study', 'day', 'index']
        constraints = [
            models.CheckConstraint(
                check = models.Q(day__gt=0) | models.Q(index__gt=0),
                name='day_or_index_gt'
            )
        ]

    def __unicode__(self):
        return '.'.join([self.study.name, str(self.day), str(self.index)])

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
    # Properties shared in both experimentations:
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, verbose_name='Registration date and time')
    birth_date = models.DateField()
    remind = models.BooleanField(default=True)
    consent = models.BooleanField(default=False)

    study = models.ForeignKey(Study, null=True, on_delete=models.CASCADE)
    sessions = models.ManyToManyField(ExperimentSession, default=[], related_name='session_stack') # FIFO
    current_session = models.ForeignKey(ExperimentSession, null=True, blank=True, on_delete=models.DO_NOTHING)
    session_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Date-time of last finished session')
    task_stack_csv = models.TextField(null=True, blank=True, default='')
    extra_json = jsonfield.JSONField(default={}, blank=True)

    class Meta:
        verbose_name = 'Participant'
        ordering = ['birth_date']

    def __unicode__(self):
        return '{} -- {}'.format(self.study.name, self.user.username)

    def __str__(self):
        return self.__unicode__()

    # HOME VIEW
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
        if not self.current_session.is_today(ref_date=self.date.date()):
            if not self.current_session.required and self.current_session.is_past(ref_datetime=self.date.date()):
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

    # END TASK VIEW :
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

    # END SESSION VIEW :
    def close_current_session(self):
        if self.sessions.all():
            self.session_timestamp = datetime.datetime.now()
            self.sessions.set(self.sessions.exclude(pk=self.current_session.pk))
            self.current_session = None
            self.save()

    def queue_reminder(self):
        if self.remind and self.sessions.all():
            day1 = self.date
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

    # CONSENT PAGE FOR NOW BUT SHOULD BE MOVED
    def assign_sessions(self, save=True):
        if self.study and ExperimentSession.objects.filter(study=self.study):
            sessions = ExperimentSession.objects.filter(study=self.study)
            self.sessions.add(*sessions)
            if save:
                self.save()
        else:
            assert False, 'No sessions found for study "{}"'.format(self.study)

    # ADDITIONAL USEFUL PROPERTIES
    @property
    def future_sessions(self):
        if self.current_session:
            if self.sessions.exclude(pk=self.current_session.pk):
                return self.sessions.exclude(pk=self.current_session.pk)
            else:
                return []
        else:
            return self.sessions.all()

    # DISPLAY USER INFORMATIONS
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



