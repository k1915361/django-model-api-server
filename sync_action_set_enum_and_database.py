import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ku_djangoo.settings')
import django
django.setup()

from polls.models import DatasetActionSet, ModelActionSet
from django.db import transaction

# python3.11 -m sync_action_set_enum_and_database

def sync_action_set(ActionSet):
    with transaction.atomic():
        ActionSet.objects.all().delete()

    ACTION_SET = ActionSet.ACTION_SET
    id = 1
    for value, label in ACTION_SET.choices:
        ActionSet.objects.create(id=id, action_type = value)
        id += 1

def sync_dataset_action_set(ActionSet=DatasetActionSet):
    sync_action_set(ActionSet)

def sync_model_action_set(ActionSet=ModelActionSet):
    sync_action_set(ActionSet)
    
sync_dataset_action_set()
sync_model_action_set()