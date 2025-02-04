import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

# ignore Question and Choice # they are templates to help structure models
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text

class Model(models.Model):
    name = models.CharField(max_length=320)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    original_model = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True) 
    
    model_type = models.CharField(max_length=320)
    model_directory = models.CharField(max_length=2048, unique=True)
    is_public = models.BooleanField(default=False) 

    description = models.CharField(max_length=320, blank=True) 
    
    created = models.DateTimeField(default=timezone.now) 
    updated = models.DateTimeField(auto_now=True) 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'user'], name='unique_model_name_user')
        ]
    
class Dataset(models.Model):
    name = models.CharField(max_length=320)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    original_dataset = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)
    
    dataset_directory = models.CharField(max_length=2048, unique=True)
    is_public = models.BooleanField(default=False)

    description = models.CharField(max_length=320, blank=True) 
    
    created = models.DateTimeField(default=timezone.now) 
    updated = models.DateTimeField(auto_now=True) 

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'user'], name='unique_dataset_name_user')
        ]

class ModelDataset(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE) 
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now) 

    class Meta:
        unique_together = ('model', 'dataset',)

class Task(models.Model):
    task_name = models.CharField(max_length=320)

# $ python3.11 -m manage makemigrations polls # ERRORS: # polls.DatasetActionSet.action_type: (fields.E005) 'choices' must be an iterable containing (actual value, human readable name) tuples.
class DatasetActionSet(models.Model):

    ACTION_SET = (
        (1, "CLEANING"),
        (2, "ANALYSIS"),
        (3, "ENRICHMENT"),
        (4, "CURATION"),
        (5, "DATA_BALANCING"),
        (6, "EXPLAINABLE_AI"),
        (None, "__empty__"),
    )
    action_type = models.IntegerField(choices=ACTION_SET, unique=True)

class DatasetAction(models.Model):
    parameters = models.JSONField() 
    action = models.ForeignKey(DatasetActionSet, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    
    def get_action_label(self):  # For easy label access
        return self.ActionType(self.action_type).label # corrected access

    @property
    def action_label(self):
        return self.action.action_type.label

class TaskAction(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    action = models.ForeignKey(DatasetAction, on_delete=models.CASCADE) 