from django.db import models
from django.utils import timezone


class Participant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.TextField()
    date = models.DateTimeField(default=timezone.now, verbose_name="Inscription Date")

    class Meta:
        verbose_name = 'Participant'
        ordering = ['date']


class Episode(models.Model):
    date = models.DateTimeField(default=timezone.now, verbose_name="Date")
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    score = models.IntegerField()
