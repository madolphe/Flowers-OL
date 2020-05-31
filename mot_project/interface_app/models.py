from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.forms import ModelForm


class ParticipantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now, verbose_name="Inscription Date")
    birth_date = models.DateField(default=datetime.date.today, blank=True, help_text='yyyy-mm-dd')
    study = models.CharField(max_length=10, default='unk')
    screen_params = models.FloatField(default=39.116)
    nb_sess_started = models.IntegerField(default=0)
    nb_sess_finished = models.IntegerField(default=0)
    nb_followups_finished = models.IntegerField(default=0)

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


class JOLD_LL_trial(models.Model):
    date = models.DateTimeField(default=timezone.now)
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    sess_number = models.IntegerField(default=0)
    trial = models.IntegerField(null=True)
    wind = models.DecimalField(decimal_places=2, max_digits=3)
    init_site = models.IntegerField(null=True)
    plat_site = models.IntegerField(null=True)
    init_dist = models.DecimalField(decimal_places=2, max_digits=5)
    end_dist = models.DecimalField(decimal_places=2, max_digits=5)
    time_trial = models.DecimalField(decimal_places=1, max_digits=8)
    time_sess = models.DecimalField(decimal_places=1, max_digits=8)
    fuel = models.IntegerField(null=True)
    presses = models.IntegerField(null=True)
    outcome = models.CharField(max_length=10)
    interruptions = models.IntegerField(null=True)


# A model to store dynamic data to display on Home Page
class DynamicProps(models.Model):
    study = models.CharField(max_length=10, default='')
    base_html = models.CharField(max_length=50, default='')
    task_url = models.CharField(max_length=50, default='')
    style = models.CharField(max_length=50, default='')
    instructions = models.CharField(max_length=50, default='')
    nb_sess = models.IntegerField(default=5)


class QBank(models.Model):
    instrument = models.CharField(max_length=100, null=True)
    component = models.CharField(max_length=100, null=True)
    group = models.CharField(max_length=100, null=True)
    handle = models.CharField(max_length=10, null=True)
    order = models.IntegerField(null=True)
    prompt = models.CharField(max_length=300, null=True)
    reverse = models.BooleanField(null=True)
    min_val = models.IntegerField(null=1)
    max_val = models.IntegerField(null=1)
    step = models.IntegerField(null=1)
    annotations = models.CharField(max_length=200, null=True)
    widget = models.CharField(max_length=30, null=True)
    sessions = models.CharField(max_length=20, null=True)


class Responses(models.Model):
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(QBank, on_delete=models.PROTECT)
    answer = models.IntegerField(null=True)
    sess = models.IntegerField(null=True)
