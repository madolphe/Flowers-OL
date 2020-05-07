from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User


class ParticipantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now, verbose_name="Inscription Date")
    birth_date = models.DateField(default=datetime.date.today, blank=True, help_text='yyyy-mm-dd')
    study = models.CharField(max_length=10, default='unk')

    class Meta:
        verbose_name = 'Participant'
        ordering = ['birth_date']


class Episode(models.Model):
    date = models.DateTimeField(default=datetime.date.today)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.CharField(max_length=20, default='[x,x]')
    # avoid creating session model:
    id_session = models.IntegerField(default=0)


class JOLD_participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wind = models.IntegerField(null=True)
    plat = models.IntegerField(null=True)
    dist = models.IntegerField(null=True)
    nb_sess_started = models.IntegerField(default=0)
    nb_sess_finished = models.IntegerField(default=0)


class JOLD_trial_LL(models.Model):
    date = models.DateTimeField(default=timezone.now)
    participant = models.ForeignKey(JOLD_participant, on_delete=models.CASCADE)
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
