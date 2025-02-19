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

class DatasetActionSet(models.Model):
    class ACTION_SET(models.TextChoices):
        CLEANING = "cleaning", _("CLEANING")
        ANALYSIS = "analysis", _("ANALYSIS")
        ENRICHMENT = "enrichment", _("ENRICHMENT")
        CURATION = "curation", _("CURATION")
        BALANCING = "balancing", _("BALANCING")
        EXPLAINABLE_AI = "explainable_ai", _("EXPLAINABLE_AI")
        UNKNOWN = _("(Unknown)")
        
    action_type = models.CharField(choices=ACTION_SET.choices)

class DatasetAction(models.Model):
    parameters = models.JSONField() 
    action = models.ForeignKey(DatasetActionSet, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    
    @property
    def action_label(self):
        return self.action.action_type.label
    
class DatasetTaskAction(models.Model):
    """
    one-many task-action.
    A task can have many actions.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    action = models.ForeignKey(DatasetAction, on_delete=models.CASCADE) 

class ModelActionSet(models.Model):
    class ACTION_SET (models.TextChoices):
        ANALYSIS = "analysis", _("ANALYSIS")
        DISTILLATION = "distillation", _("DISTILLATION")
        FINE_TUNING = "fine_tuning", _("FINE_TUNING")
        EXPLAINABLE_AI = "explainable_ai", _("EXPLAINABLE_AI")
        UNKNOWN = _("(Unknown)")
    
    action_type = models.CharField(choices=ACTION_SET.choices, unique=True)

class ModelAction(models.Model):
    parameters = models.JSONField() 
    action = models.ForeignKey(ModelActionSet, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    
    @property
    def action_label(self):
        return self.action.action_type.label
    
class ModelTaskAction(models.Model):
    """
    one-many task-action.
    A task can have many actions.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    action = models.ForeignKey(ModelAction, on_delete=models.CASCADE) 
