from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class ParticipantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now, verbose_name="Inscription Date")
    birth_date = models.DateField(default=datetime.date.today, blank=True)

    class Meta:
        verbose_name = 'Participant'
        ordering = ['birth_date']


# Send a signal when a new user is created so that extra-information could be add (whenever a save event occurs)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ParticipantProfile.objects.create(user=instance)



@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Episode(models.Model):
    date = models.DateTimeField(datetime.date.today)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()


