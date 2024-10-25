import datetime

from django.db import models
from django.utils import timezone

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

class Login(models.Model): # Django already has user database with password encryption. DELETE this if no longer used.
    email = models.EmailField(max_length=320)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=255)

    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True) 

class Net_Model(models.Model):
    name = models.CharField(max_length=320)
    owner_id = models.ForeignKey(Login, on_delete=models.CASCADE) 

    model_type = models.CharField(max_length=320)
    model_url = models.CharField(max_length=2048)

    meta_description = models.CharField(max_length=320) # brief description on search result page
    description = models.CharField(max_length=200_000) 
    
    created = models.DateTimeField(default=timezone.now) 
    updated = models.DateTimeField(auto_now=True) # retrain finish date. successor creation date. 

    # no_of_parameter = models.IntegerField(default=0) 
    # train_time = DurationField(default=0) # time took to train or retrain the model 
    