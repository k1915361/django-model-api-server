import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

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

    model_type = models.CharField(max_length=320)
    file_path = models.CharField(max_length=2048)
    is_public = models.BooleanField(default=False) 

    description = models.CharField(max_length=320, blank=True) 
    
    created = models.DateTimeField(default=timezone.now) 
    updated = models.DateTimeField(auto_now=True) # retrain finish date. successor creation date. 

    # no_of_parameter = models.IntegerField(default=0) 
    # train_time = DurationField(default=0) # time took to train or retrain the model 
    
class Dataset(models.Model):
    name = models.CharField(max_length=320)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    
    dataset_directory = models.CharField(max_length=2048)
    is_public = models.BooleanField(default=False)

    description = models.CharField(max_length=320, blank=True) 
    
    created = models.DateTimeField(default=timezone.now) 
    updated = models.DateTimeField(auto_now=True) 

class Image_Dataset(models.Model):
    name = models.CharField(max_length=320)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    
    dataset_directory = models.CharField(max_length=2048)
    is_public = models.BooleanField(default=False)

    description = models.CharField(max_length=320, blank=True) 
    
    created = models.DateTimeField(default=timezone.now) 
    updated = models.DateTimeField(auto_now=True) 

class CSV_Dataset(models.Model):
    name = models.CharField(max_length=320)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    
    dataset_directory = models.CharField(max_length=2048)
    is_public = models.BooleanField(default=False)

    description = models.CharField(max_length=320, blank=True) 
    
    created = models.DateTimeField(default=timezone.now) 
    updated = models.DateTimeField(auto_now=True) 