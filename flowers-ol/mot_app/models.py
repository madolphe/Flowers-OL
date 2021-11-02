from django.db import models
import datetime
from django.contrib.auth.models import User
from manager_app.models import ParticipantProfile
import jsonfield


class Episode(models.Model):
    # Foreign key to user :
    participant = models.ForeignKey(User, on_delete=models.CASCADE)

    # Description of the task
    date = models.DateTimeField(auto_now_add=True)
    secondary_task = models.CharField(max_length=20, default='none')
    episode_number = models.IntegerField(default=0)

    # Task parameters:
    n_distractors = models.IntegerField(default=0)
    n_targets = models.IntegerField(default=0)
    angle_max = models.IntegerField(default=0)
    angle_min = models.IntegerField(default=0)
    radius = models.FloatField(default=0)
    speed_min = models.FloatField(default=0)
    speed_max = models.FloatField(default=0)
    RSI = models.FloatField(default=0)
    SRI_max = models.FloatField(default=0)
    presentation_time = models.FloatField(default=0)
    fixation_time = models.FloatField(default=0)
    tracking_time = models.FloatField(default=0)
    probe_time = models.FloatField(default=0)
    idle_time = models.FloatField(default=0)

    # User Score:
    nb_target_retrieved = models.IntegerField(default=0)
    nb_distract_retrieved = models.IntegerField(default=0)

    # To avoid creating session model but to be able to make joint queries:
    id_session = models.IntegerField(default=0)
    finished_session = models.BooleanField(default=False)

    @property
    def get_results(self):
        if self.nb_target_retrieved == self.n_targets and \
                self.nb_distract_retrieved == self.n_distractors:
            return 1
        return 0

    def __unicode__(self):
        return str(self.episode_number)

    def __str__(self):
        return self.__unicode__()


class SecondaryTask(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, default='detection')
    delta_orientation = models.FloatField(default=0)
    success = models.BooleanField(default=False)
    answer_duration = models.FloatField(default=0)


class CognitiveTask(models.Model):
    name = models.TextField(blank=True)
    view_name = models.TextField(blank=True)
    instructions_prompt_label = models.TextField(blank=True)
    template_instruction_path = models.TextField(blank=True)
    template_tutorials_path = models.TextField(blank=True)


class CognitiveResult(models.Model):
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    cognitive_task = models.ForeignKey(CognitiveTask, on_delete=models.CASCADE)
    idx = models.IntegerField()
    results = jsonfield.JSONField(blank=True)
    status = models.TextField(blank=True, default="pre_test")
