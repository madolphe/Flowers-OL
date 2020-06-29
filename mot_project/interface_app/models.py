from django.db import models
from django.utils import timezone
import datetime, uuid, json
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.validators import validate_comma_separated_integer_list
import jsonfield

class Study(models.Model):
    name = models.CharField(max_length=50, default=uuid.uuid4, unique=True)
    project = models.CharField(max_length=100, default='')
    base_template = models.CharField(max_length=50, default='base.html')
    style = models.CharField(max_length=50, null=True)
    briefing_template = models.CharField(max_length=50, null=True)
    extra_json = jsonfield.JSONField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Study'
        verbose_name_plural = 'Studies'


class Task(models.Model):
    name = models.CharField(max_length=50, default='', unique=True)
    description = models.TextField(default='')
    prompt = models.CharField(max_length=100, default='', blank=True)
    view_name = models.CharField(max_length=50, default='')
    info_templates_csv = models.TextField(null=True, blank=True)
    extra_json = jsonfield.JSONField()

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
    study = models.ForeignKey(Study, to_field='name', null=True, on_delete=models.SET_NULL)
    day = models.IntegerField(default=0) # have to use default=0 because nulls are not compared for uniqueness
    index = models.IntegerField(default=0)
    wait = models.DurationField(default=datetime.timedelta(0))
    tasks_csv = models.CharField(max_length=200, default='')
    extra_json = jsonfield.JSONField()

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
        return [Task.objects.get(name=task_name) for task_name in self.tasks_csv.split(',')]

    def get_task_by_index(self, index):
        return Task.objects.get(name=self.tasks_csv.split(',')[index])


class ParticipantProfile(models.Model):
    # Properties shared in both experimentations:
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    screen_params = models.FloatField(default=39.116)
    date = models.DateTimeField(default=timezone.now, verbose_name='Registration Date')
    birth_date = models.DateField(default=datetime.date.today, blank=True, help_text='day / month / year')
    study = models.ForeignKey(Study, null=True, on_delete=models.CASCADE)
    consent = models.BooleanField(default=False)
    sessions = models.ManyToManyField(ExperimentSession, default=[], related_name='session_stack') # FIFO
    current_session = models.ForeignKey(ExperimentSession, null=True, blank=True, on_delete=models.DO_NOTHING)
    session_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Date-time of last finished session')
    task_stack_csv = models.TextField(null=True, blank=True, default='')
    extra_json = jsonfield.JSONField()

    # ZPDES-exp extra infos:
    screen_params = models.FloatField(null=True)
    sexe = models.CharField(max_length=20, choices=(("Femme", "Femme"), ("Homme", "Homme"), ("Autre", "Autre")),
                            null=True)
    job = models.CharField(max_length=40, null=True)
    # Frequency of video games practice is a Response model
    video_game_start = models.IntegerField(null=True)
    # For vide_game_freq, vid_game_habit and driving_freq, custom widget would be used
    # ( a question object is passed to ModelForm and the widget is set up )
    video_game_freq = models.CharField(max_length=40, null=True) # range : "Never, sometimes, often, daily"
    video_game_habit = models.CharField(max_length=40, null=True) # range : "Action, Sport, FPS, RPG, MMO"
    driver = models.BooleanField(null=False, default=True, choices=((True, "Oui"), (False, "Non")))
    driving_start = models.IntegerField(null=True)
    driving_freq = models.CharField(max_length=40, null=True) # range : "Never, sometimes, once a week, daily"
    attention_training = models.BooleanField(null=True, default=True, choices=((True, "Oui"), (False, "Non")))
    online_training = models.BooleanField(null=True, default=True, choices=((True, "Oui"), (False, "Non")))

    class Meta:
        verbose_name = 'Participant'
        ordering = ['birth_date']

    def assign_condition(self):
        pass

    def assign_sessions(self, save=True):
        if self.study and ExperimentSession.objects.filter(study=self.study):
            sessions = ExperimentSession.objects.filter(study=self.study)
            self.sessions.add(*sessions)
            if save: self.save()
        else:
            assert False, 'No sessions found for study "{}"'.format(self.study)

    def set_current_session(self):
        assert self.sessions.all(), 'Participant has no sessions assigned'
        s = self.sessions.first()
        if self.current_session == s:
            return
        else:
            self.current_session = None
        if s.day:
            today = datetime.date.today()
            day1 = self.date.date()
            if today != day1 + datetime.timedelta(days=s.day-1):
                return
        if self.session_timestamp and s.wait:
            now = datetime.datetime.now()
            if now - self.session_timestamp < s.wait:
                return
        self.current_session = s
        self.task_stack_csv = s.tasks_csv
        self.save()

    @property
    def future_sessions(self):
        if self.current_session:
            return self.sessions.exclude(pk=self.current_session.pk)
        else: return self.sessions.all()

    def pop_session(self):
        if self.sessions:
            self.sessions = self.sessions.exclude(pk=self.sessions.first().pk)
        self.save()

    @property
    def task_stack(self):
        # The first (empty) split removes whitespaces
        task_names = self.task_stack_csv.split().split(',')
        print(task_names)
        return tuple([Task.objects.get(name=name) for name in task_names])

    @property
    def current_task(self):
        if not self.task_stack_csv:
            return None
        stack_head = self.task_stack_csv.split(',')[0]
        return Task.objects.get(name=stack_head)

    def pop_task(self, n=1):
        """Remove n items from task "stack". Return False if updated stack is empty, True otherwise"""
        task_names = self.task_stack_csv.split(',')[n:]
        self.task_stack_csv = ','.join(task_names)
        self.save()
        print(self.task_stack_csv)

    @property
    def progress_info(self):
        l = []
        for i, session in enumerate(ExperimentSession.objects.filter(study=self.study), 1):
            sess_info = {'num': i,
                         'current': True if session == self.current_session else False,
                         'tasks': [task.description for task in session.get_task_list()]}
            l.append(sess_info)
        return l


class Episode(models.Model):
    # Foreign key to user :
    participant = models.ForeignKey(User, on_delete=models.CASCADE)

    # Description of the task
    date = models.DateTimeField(default=datetime.date.today)
    secondary_task = models.CharField(max_length=20, default='none')
    episode_number = models.IntegerField(default=0)

    # Task parameters:
    n_distractors = models.IntegerField(default=0)
    n_targets = models.IntegerField(default=0)
    angle_max = models.IntegerField(default=0)
    angle_min = models.IntegerField(default=0)
    radius = models.IntegerField(default=0)
    speed_min = models.FloatField(default=0)
    speed_max = models.FloatField(default=0)
    RSI = models.FloatField(default=0)
    SRI_max = models.FloatField(default=0)
    presentation_time = models.FloatField(default=0)
    fixation_time = models.FloatField(default=0)
    tracking_time = models.FloatField(default=0)

    # User Score:
    nb_target_retrieved = models.IntegerField(default=0)
    nb_distract_retrieved = models.IntegerField(default=0)

    # To avoid creating session model but to be able to make joint queries:
    id_session = models.IntegerField(default=0)
    finished_session = models.BooleanField(default=False)


class SecondaryTask(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, default='detection')
    delta_orientation = models.FloatField(default=0)
    success = models.BooleanField(default=False)
    answer_duration = models.FloatField(default=0)


class JOLD_LL_trial(models.Model):
    date = models.DateTimeField(default=timezone.now)
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    session = models.ForeignKey(ExperimentSession, null=True, on_delete=models.CASCADE)
    trial = models.IntegerField(null=True)
    wind = models.DecimalField(decimal_places=2, max_digits=3)
    init_site = models.IntegerField(null=True)
    plat_site = models.IntegerField(null=True)
    init_dist = models.DecimalField(decimal_places=2, max_digits=5)
    end_dist = models.DecimalField(decimal_places=2, max_digits=5)
    time_trial = models.DecimalField(decimal_places=1, max_digits=8)
    time_block = models.DecimalField(decimal_places=1, max_digits=8)
    fuel = models.IntegerField(null=True)
    presses = models.IntegerField(null=True)
    outcome = models.CharField(max_length=10)
    interruptions = models.IntegerField(null=True)
    forced = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Lunar lander trial'
        verbose_name_plural = 'Lunar lander trials'


class Question(models.Model):
    instrument = models.CharField(max_length=100, null=True)
    component = models.CharField(max_length=100, null=True)
    group = models.CharField(max_length=50, null=True)
    handle = models.CharField(max_length=10, null=True)
    order = models.IntegerField(null=True)
    prompt = models.CharField(max_length=300, null=True)
    reverse = models.BooleanField(null=True)
    min_val = models.IntegerField(null=1)
    max_val = models.IntegerField(null=1)
    step = models.IntegerField(null=1)
    annotations = models.CharField(max_length=200, null=True)
    widget = models.CharField(max_length=30, null=True)

    def __unicode__(self):
        return self.handle

    def __str__(self):
        return self.__unicode__()


class Answer(models.Model):
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    session = models.ForeignKey(ExperimentSession, null=True, on_delete=models.DO_NOTHING)
    value = models.IntegerField(null=True)
