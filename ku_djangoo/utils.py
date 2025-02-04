import os
from ku_djangoo.settings import ROOT_MODEL_DIR, ROOT_DATASET_DIR

def get_unique_directory(root_dir: str, user_id: str, name: str):
    save_directory = os.path.join(root_dir, user_id, name)
    return save_directory

def get_unique_model_directory(user_id: str, model_name: str, root_dir: str = ROOT_MODEL_DIR):
    return get_unique_directory(root_dir, user_id, model_name) 

def get_unique_dataset_directory(user_id: str, dataset_name: str, root_dir: str = ROOT_DATASET_DIR):
    return get_unique_directory(root_dir, user_id, dataset_name) 
