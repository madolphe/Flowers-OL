from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.validators import validate_comma_separated_integer_list


class Study(models.Model):
    """ Study model specifies various attributes of a study needed to run it """
    name = models.CharField(max_length=10, null=True)
    project = models.CharField(max_length=100, null=True)
    base_template = models.CharField(max_length=50, default='base.html')
    task_url = models.CharField(max_length=50, null=True)
    style = models.CharField(max_length=50, null=True)
    instructions = models.CharField(max_length=50, null=True)
    tutorial = models.CharField(max_length=50, default='')
    consent_text = models.CharField(max_length=50, null=True)
    nb_sessions = models.IntegerField(default=5)
    spacing = models.CharField(max_length=100, default='[1]', validators=[validate_comma_separated_integer_list])


class ParticipantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now, verbose_name="Registration Date")
    birth_date = models.DateField(default=datetime.date.today, blank=True, help_text='day / month / year')
    study = models.ForeignKey(Study, null=True, on_delete=models.CASCADE)
    screen_params = models.FloatField(default=39.116)
    nb_practice_blocks_started = models.IntegerField(default=0)
    nb_practice_blocks_finished = models.IntegerField(default=0)
    nb_question_blocks_finished = models.IntegerField(default=0)
    consent = models.BooleanField(default=False)

    # JOLD properties
    wind = models.IntegerField(null=True)
    plat = models.IntegerField(null=True)
    dist = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'Participant'
        ordering = ['birth_date']


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


class ExperimentSession(models.Model):
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    num = models.IntegerField(default=1)
    practice_finished = models.BooleanField(default=False)
    questions_finished = models.BooleanField(null=True)
    is_finished = models.BooleanField(default=False)


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


class Question(models.Model):
    instrument = models.CharField(max_length=100, null=True)
    component = models.CharField(max_length=100, null=True)
    group = models.IntegerField(null=True)
    handle = models.CharField(max_length=10, null=True)
    order = models.IntegerField(null=True)
    prompt = models.CharField(max_length=300, null=True)
    reverse = models.BooleanField(null=True)
    min_val = models.IntegerField(null=1)
    max_val = models.IntegerField(null=1)
    step = models.IntegerField(null=1)
    annotations = models.CharField(max_length=200, null=True)
    widget = models.CharField(max_length=30, null=True)
    session_list = models.CharField(max_length=20, default='', validators=[validate_comma_separated_integer_list])


class Answer(models.Model):
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    session = models.ForeignKey(ExperimentSession, null=True, on_delete=models.CASCADE)
    value = models.IntegerField(null=True)
