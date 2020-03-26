from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User


class ParticipantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now, verbose_name="Inscription Date")
    birth_date = models.DateField(default=datetime.date.today, blank=True)

    class Meta:
        verbose_name = 'Participant'
        ordering = ['birth_date']


class Episode(models.Model):
    date = models.DateTimeField(datetime.date.today)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    # avoid creating session model:
    # id_session = models.IntegerField()

