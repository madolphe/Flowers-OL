from django.db import models
import datetime
from manager_app.models import ParticipantProfile, ExperimentSession


# Create your models here.
class JOLD_LL_trial(models.Model):
    date = models.DateTimeField(default=datetime.datetime.now)
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
