from django import forms
from django.db.models import Q
from django.db.models import F
from django.http import HttpResponseRedirect
from .models import Dataset, Model, ModelDataset, Question, Choice
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template import Context, Template
from django.core.files.uploadhandler import MemoryFileUploadHandler, TemporaryFileUploadHandler
from django.core.files.storage import FileSystemStorage
import re
import os
import ast
import datetime
import shutil  

ROOT_DATASET_DIR = 'asset/user/dataset/'
ROOT_MODEL_DIR = 'asset/user/model/'
ROOT_TEMP = 'asset/temp/test'

is_public_map_bool = {
    '1': False, '2': True, 
    1: False, 2: True,
    False: '1', True: '2',
}

is_public_map_label = {
    '1': 'private', '2': 'public', 
    'private' :'1', 'public': '2', 
}

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

class UploadDatasetForm(forms.Form):
    name = forms.CharField(max_length=320)
    dataset = forms.FileField(required=False)
    zipfile = forms.FileField(required=False)  
    directories = forms.CharField(required=False)
    filepaths = forms.FilePathField(path=f"{ROOT_DATASET_DIR}/", recursive=True, allow_files=True, allow_folders=True, required=False)

    CHOICES = [
        ('1', 'private'),
        ('2', 'public'),
    ]

    is_public = forms.ChoiceField(
        label="Publicity",
        widget=forms.RadioSelect,
        choices=CHOICES, 
        required=False,
    )

class ChooseModelForkForm(forms.Form):
    model_id = forms.IntegerField(widget=forms.HiddenInput())
    
class UploadModelForm(forms.Form):
    CHOICES = [
        ('1', 'private'),
        ('2', 'public'),
    ]

    model_folder = forms.FileField()
    name = forms.CharField(max_length=320)
    model_type = forms.CharField(max_length=320)
    description = forms.CharField(max_length=320, required=False)
    is_public = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHOICES, 
    )

class UserDatasetListPathsForm(forms.Form):
    def __init__(self, userid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.userid = userid

        self.fields['filepaths_public'] = forms.FilePathField(
            path=f"{ROOT_DATASET_DIR}/",
            recursive=True,
            allow_files=True,
            allow_folders=True,
            required=False,
        )

        self.fields['filepaths_private'] = forms.FilePathField(
            path=f"{ROOT_DATASET_DIR}/",
            recursive=True,
            allow_files=True,
            allow_folders=True,
            required=False,
        )
    
class PublicDatasetListPaginationView(forms.Form):
    paginate_by = 10
    dataset = Dataset    

class PrivateDatasetListPaginationView(forms.Form):
    paginate_by = 10
    dataset = Dataset

class PublicModelListPaginationView(forms.Form):
    paginate_by = 10
    model = Model

class PrivateModelListPaginationView(forms.Form):
    paginate_by = 10
    model = Model

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def login_message_view(request, context={"please_login_message": "Please login to see this page."}):
    return login_view(request, context=context)

def profile_view(request):
    base_html = get_base_html(request.user.is_authenticated)    
    
    if not request.user.is_authenticated:
        return login_message_view(request)

    return render(request, "polls/profile.html")

def register_view(request, context={}):
    template_name = "registration/register_view.html"
    return render(request, template_name, context)

def register_retry_view(request, context={'retry_register_message': 'Your username or email is already taken. Please try again.'}):
    return register_view(request, context)

def make_user_directories(user_id: str):
    for root_directory in [ROOT_DATASET_DIR, ROOT_MODEL_DIR]:
        for publicity in ['private', 'public']:
            os.makedirs(os.path.join(root_directory, publicity, user_id), exist_ok=True)

def register(request):
    username = request.POST["username"]
    email = request.POST["email"]
    
    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        return redirect("/polls/register-retry-view/")
    
    password = request.POST["password"]

    user = User.objects.create_user(username, email, password)
    user.save()

    make_user_directories(str(user.id))

    login(request, user)
    return redirect('/polls/profile/')

def login_view(request, context={}):
    template_name = "registration/login_view.html"
    return render(request, template_name, context)

def login_retry_view(request, context={'retry_login_message': 'Login was incorrect. Please try again.'}):
    return login_view(request, context)

def login_user(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None or request.user.is_authenticated:
        login(request, user)
        return redirect('/polls/home/')
    
    return redirect('/polls/login-retry-view/')

def get_base_html(user_is_authenticated):
    if user_is_authenticated:
        return "base_logged_in.html"
    elif not user_is_authenticated:
        return "base_login_register_search.html"

def public_dataset_list_view(request, context={}):
    template_name = "polls/public_dataset_list_view.html"
    base_html = get_base_html(request.user.is_authenticated)
    
    dataset_list = Dataset.objects.filter(is_public=True).order_by("-created")
    paginator = Paginator(dataset_list, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = { 'base_html': base_html, 'page_obj': page_obj }

    if request.method != "POST":
        context['form'] = PublicDatasetListPaginationView()
        return render(request, template_name, context)

    context['form'] = PublicDatasetListPaginationView()
    return render(request, template_name, context)

def private_dataset_list_view(request, context={}):
    template_name = "polls/private_dataset_list_view.html"
    base_html = get_base_html(request.user.is_authenticated)

    dataset_list = Dataset.objects.filter(is_public=False, user=request.user).order_by("-created")
    paginator = Paginator(dataset_list, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = { 'base_html': base_html, 'page_obj': page_obj }

    context['form'] = PrivateDatasetListPaginationView()
    return render(request, template_name, context)

def public_model_list_view(request, context={}):
    template_name = "polls/public_model_list_view.html"
    base_html = get_base_html(request.user.is_authenticated)
    
    model_list = Model.objects.filter(is_public=True).order_by("-created")
    paginator = Paginator(model_list, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = { 'base_html': base_html, 'page_obj': page_obj }

    if request.method != "POST":
        context['form'] = PublicModelListPaginationView()
        return render(request, template_name, context)

    context['form'] = PublicModelListPaginationView()
    return render(request, template_name, context)

def private_model_list_view(request, context={}):
    template_name = "polls/private_model_list_view.html"
    base_html = get_base_html(request.user.is_authenticated)

    model_list = Model.objects.filter(is_public=False, user=request.user).order_by("-created")
    paginator = Paginator(model_list, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = { 'base_html': base_html, 'page_obj': page_obj }

    context['form'] = PrivateModelListPaginationView()
    return render(request, template_name, context)

def index_homepage_view(request):
    template_name = "polls/index.html"
    base_html = get_base_html(request.user.is_authenticated)
    
    dataset_list = Dataset.objects.filter(is_public=True).order_by("-created")
    paginator = Paginator(dataset_list, 2)
    page_number = request.GET.get("dataset_page")
    dataset_page_obj = paginator.get_page(page_number)

    model_list = Model.objects.filter(is_public=True).order_by("-created")
    model_paginator = Paginator(model_list, 2)
    model_page_number = request.GET.get("model_page")
    model_page_obj = model_paginator.get_page(model_page_number)

    context = { 
        'base_html': base_html, 
        'dataset_page_obj': dataset_page_obj,
        'model_page_obj': model_page_obj,
    }

    if request.user.is_authenticated:
        private_dataset_list = Dataset.objects.filter(is_public=False, user=request.user).order_by("-created")
        context['dataset_private_page_obj'] = private_dataset_list

        private_model_list = Model.objects.filter(is_public=False, user=request.user).order_by("-created")
        context['model_private_page_obj'] = private_model_list

    return render(request, template_name, context)

def user_dataset_list_path_view(request, context={}):
    template_name = "polls/user_dataset_list_path_view.html"
    base_html = get_base_html(request.user.is_authenticated)
    context = {'base_html': base_html}

    if request.method != "POST":
        context['form'] = UserDatasetListPathsForm(request.user.id)
        return render(request, template_name, context)
    
    context['form'] = UserDatasetListPathsForm(request.user.id, request.POST, request.FILES)
    return render(request, template_name, context)
    
def handle_uploaded_file(f, filename='afile', dir="asset/user/dataset/", file_extension=''):
    with open(os.path.join(dir, f"{filename}{file_extension}"), "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def now_Ymd_HMS(format='%Y%m%d_%H%M%S') -> str:
    return timezone.now().strftime(format)

def get_home_directory(directories):
    for directory in directories:
        for sep in ['/', '\\\\', '\\']:
            if sep in directory:
                return directory.split(sep)[0]
    return ''

def unzip_and_save(zipfile_dir, name, user, ispublic, timestamp):
    return

def save_dataset_to_database(name: str, user: User, dataset_directory: str, ispublic):
    dataset = Dataset(name=name, user=user, dataset_directory=dataset_directory, is_public=is_public_map_bool[ispublic])
    dataset.save()
    return

def save_zip_file(zipfile, name: str, user: User, ispublic: str, timestamp: str, root_dir: str = ROOT_DATASET_DIR):
    save_filename = f"{user.id}-{timestamp}-{zipfile.name}"
    zipfile_dir = os.path.join(root_dir, save_filename)

    FileSystemStorage(location=root_dir).save(save_filename, zipfile) 
    save_dataset_to_database(name, user, zipfile_dir, ispublic)
    return zipfile_dir

def save_model_folder_info_to_database(name: str, user: User, model_type: str, model_directory: str, ispublic: str, original_model: Model = None, description: str = ""):
    model = Model(
        name=name, 
        user=user, 
        model_type=model_type, 
        model_directory=model_directory,
        original_model=original_model,
        is_public=is_public_map_bool[ispublic],
        description=description,
    )
    model.save()
    return model

def save_dataset_folder_info_to_database(name: str, user: User, dataset_directory: str, ispublic: str):
    dataset = Dataset(
        name=name, 
        user=user, 
        dataset_directory=dataset_directory, 
        is_public=is_public_map_bool[ispublic],
    )
    dataset.save()
    return dataset

def save_folder(files: list, directories: dict, user: User, timestamp: str, root_dir: str = ROOT_DATASET_DIR, name: str = ""):
    home_directory = get_home_directory(directories.values())
    dataset_dir_unique = os.path.join(root_dir, f"{user.id}-{timestamp}")
    dataset_dir = f"{dataset_dir_unique}-{home_directory}"
    
    for file in files:
        relative_file_path = directories.get(file.name)
        relative_file_directory, _ = os.path.split(relative_file_path)
        
        file_dir = f"{dataset_dir_unique}-{relative_file_directory}"
        os.makedirs(file_dir, exist_ok=True)
        
        handle_uploaded_file(file, filename=file.name, dir=file_dir)
    
    return dataset_dir

def upload_folder(request, template_name = "polls/upload_folder.html", context = {}):
    if request.method != "POST":
        form = UploadDatasetForm()
        return render(request, template_name, {"form": form} | context)
    
    form = UploadDatasetForm(request.POST, request.FILES)
    ispublic = request.POST.get("is_public")
    
    name = request.POST.get("name")
    directories_str = request.POST.get("directories")
    
    if directories_str:
        directories_dict = ast.literal_eval(directories_str)

    zipfile_list = request.FILES.getlist('zipfile')

    if len(zipfile_list) != 0:
        zipfile = zipfile_list[0] 

        timestamp = now_Ymd_HMS()
        zipfile_dir = save_zip_file(zipfile, name, request.user, ispublic, timestamp)
        
        unzip_and_save(zipfile_dir, name, request.user, ispublic, timestamp)

    dataset_folder = request.FILES.getlist('file')

    if form.is_valid() and len(dataset_folder) != 0 and len(directories_dict) != 0:
        timestamp = now_Ymd_HMS()
        dataset_dir = save_folder(dataset_folder, directories_dict, request.user, timestamp, root_dir=ROOT_DATASET_DIR)
        save_dataset_folder_info_to_database(name, request.user, dataset_dir, ispublic)

    return render(request, template_name, {"form": form} | context)

def timestamp_humanize(timestamp: datetime) -> str:
    """
    Formats a timestamp string into a human-readable format.

    Args:
        timestamp (str): The timestamp string in a suitable format (e.g., ISO 8601).

    Returns:
        str: The formatted timestamp string.
    """
    
    timestamp = timestamp.replace(tzinfo=None)

    now = datetime.datetime.now()
    time_diff = now - timestamp

    if time_diff.days == 0:
        if time_diff.seconds < 60:
            return f"{time_diff.seconds} seconds"
        if time_diff.seconds < 3600:
            return f"{time_diff.seconds // 60} minutes"
        else:
            return f"{time_diff.seconds // 3600} hours"
    elif time_diff.days < 7:
        return f"{time_diff.days} days"
    elif time_diff.days < 30:
        return f"{timestamp.strftime('%d %b')}"
    else:
        return f"{timestamp.strftime('%d %b %Y')}"

def model_list_view_to_fork(request):
    template_name = "polls/model_list_choose_one_to_fork.html"
    public_model_list = Model.objects.filter(is_public=True).order_by("-created")
    context = {'public_model_list': public_model_list}

    if request.method != "POST":
        form = ChooseModelForkForm()
        return render(request, template_name, {"form": form} | context)
    
    form = ChooseModelForkForm(request.POST)
    chosen_model_id = request.POST.get('model_id')

    name = request.POST.get("name")
    model_type = request.POST.get("model_type")
    ispublic = request.POST.get("is_public")
    description = request.POST.get("description")

    fork_model(chosen_model_id, request.user, name, model_type, ispublic, description=description)

    return render(request, template_name, {"form": form} | context)

def separate_original_folder_name(string: str) -> tuple:
    """
    in example
    "1-20241010_101010-CS_modelA"
    
    out
    ("1-20241010_101010-", "CS_modelA")
    """

    match = re.match(r"(\d+-\d{8}_\d{6}-)(.+)", string)
    if match:
        return match.group(1), match.group(2)
    else:
        return None
    
def fork_model(model_id, user, name, model_type, ispublic, description=""):
    chosen_model = Model.objects.filter(id=model_id).first()
    
    timestamp = now_Ymd_HMS()

    root_dir = ROOT_MODEL_DIR
    home_directory = chosen_model.model_directory
    model_dir_unique = os.path.join(root_dir, f"{user.id}-{timestamp}")
    
    home_directory_folder_name = os.path.basename(home_directory) 
    parts = separate_original_folder_name(home_directory_folder_name)
    original_folder_name = parts[1]

    model_directory = f"{model_dir_unique}-{original_folder_name}"

    result = copy_directory(chosen_model.model_directory, model_directory)

    if result == "OSError copy directory":
        return

    model = save_model_folder_info_to_database(name, user, model_type, model_directory, 
        ispublic, original_model=chosen_model, description=description)

    return model

def copy_directory(src: str, dest: str):
    try:
        shutil.copytree(src, dest)
    except OSError as err:
        print("OSError - copy_directory() - fail to copy directory: % s" % err)
        return "OSError copy directory"
    return

def upload_model(request):
    if request.method != "POST":
        form = UploadModelForm()
        return render(request, "polls/upload_model.html", {"form": form})

    form = UploadModelForm(request.POST, request.FILES)
    name = request.POST.get("name")
    model_type = request.POST.get("model_type")
    ispublic = request.POST.get("is_public")
    directories_str = request.POST.get("directories")
    description = request.POST.get("description")
    model_folder = request.FILES.getlist('model_folder')

    if directories_str:
        directories_dict = ast.literal_eval(directories_str)

    if form.is_valid() and len(model_folder) != 0 and len(directories_dict) != 0: 
        timestamp = now_Ymd_HMS()
        model_directory = save_folder(model_folder, directories_dict, request.user, timestamp, root_dir=ROOT_MODEL_DIR)
        save_model_folder_info_to_database(name, request.user, model_type, model_directory, ispublic, description=description)
        
    return render(request, "polls/upload_model.html", {"form": form})

def personal_dataset_repo_view(request):
    if not request.user.is_authenticated:
        return redirect('/polls/login-view/')

    template_name = "polls/personal_dataset_repo.html"
    dataset = Dataset.objects.filter(is_public=False, user=request.user).annotate(
        updated_str = F('updated')
    ).order_by("-created")
    
    for datast in dataset:
        datast.updated_str = timestamp_humanize(datast.updated_str)

    context = {'private_dataset_list': dataset}
    return upload_folder(request, template_name, context)

def model_list_choose_one_to_relate_a_dataset(request):
    template_name = "polls/model_list_choose_one_to_relate_a_dataset.html" 
    public_model_list = Model.objects.filter(is_public=True).order_by("-created")
    context = {'public_model_list': public_model_list}

    if request.method != "POST":
        return render(request, template_name, context)
    
    chosen_model_id = request.POST.get('model_id')
    context['chosen_model_id'] = chosen_model_id
    context['chosen_model'] = Model.objects.filter(id=chosen_model_id).first()
    context['public_dataset_list'] = Dataset.objects.filter(is_public=True).order_by("-created")

    print(' --- ', context['chosen_model_id'])

    return render(request, "polls/dataset_list_choose_to_relate_a_model.html" , context)

def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)

@login_required(login_url='/polls/login')
def view_user_private_models(request):
    pass

def logout_view(request):
    logout(request)
    return redirect("/polls/")

def get_queryset(self):
    """
    Return the last five published questions (not including those set to be
    published in the future).
    """
    return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
        :5
    ]

def process_model_options_view(request):
    if not request.user.is_authenticated:
        return redirect('/polls/login-view/')
    
    template_name = "polls/process_model_options.html"
    dataset_list = Dataset.objects.filter(is_public=True).order_by("-created")
    model_list = Model.objects.filter(is_public=True).order_by("-created")
    private_dataset_list = Dataset.objects.filter(is_public=False, user=request.user).order_by("-created")
    private_model_list = Model.objects.filter(is_public=False, user=request.user).order_by("-created")

    context = {
        "public_dataset_list": dataset_list,
        "public_model_list": model_list,
        'private_dataset_list': private_dataset_list,
        'private_model_list': private_model_list,
    }

    if request.method != 'POST':
        return render(request, template_name, context=context)

    model_id = request.POST.get("model_id")
    dataset_id = request.POST.get("dataset_id")
    uploaded_dataset = request.FILES.getlist("form_dataset_folder")
    uploaded_model = request.FILES.getlist("form_model_folder")
    dataset_directories_str = request.POST.get("dataset_folder_directories")
    model_directories_str = request.POST.get("model_folder_directories")
    model_name = request.POST.get("model_name")
    model_type = request.POST.get("model_type")
    model_ispublic = request.POST.get("model_is_public")
    
    dataset_name = request.POST.get("dataset_name")
    dataset_ispublic = request.POST.get("dataset_is_public")
    
    if model_directories_str:
        model_directories_dict = ast.literal_eval(model_directories_str)

    if dataset_directories_str:
        dataset_directories_dict = ast.literal_eval(dataset_directories_str)

    timestamp = now_Ymd_HMS()

    print(' - uploaded_dataset - ', uploaded_dataset)
    print(' - uploaded_model - ', uploaded_model)
    print(' - dataset_directories - ', dataset_directories_str)
    print(' - model_directories - ', model_directories_str)

    if len(uploaded_model) != 0 and len(model_directories_dict) != 0 and model_name and model_type and model_ispublic: 
        print(' - uploaded model ')
        model_directory = save_folder(uploaded_model, model_directories_dict, request.user, timestamp, root_dir=ROOT_MODEL_DIR)
        model = save_model_folder_info_to_database(model_name, request.user, model_type, model_directory, model_ispublic)
    
    elif len(uploaded_model) == 0:
        print(' - no uploaded model ')
        model = Model.objects.filter(id=model_id).first()
        context['chosen_model'] = model
    
    if len(uploaded_dataset) != 0 and len(dataset_directories_dict) != 0 and dataset_name and dataset_ispublic:
        print(' - uploaded dataset ')
        dataset_directory = save_folder(uploaded_dataset, dataset_directories_dict, request.user, timestamp, root_dir=ROOT_DATASET_DIR)
        dataset = save_dataset_folder_info_to_database(dataset_name, request.user, dataset_directory, dataset_ispublic)

    elif len(uploaded_dataset) == 0:
        print(' - no uploaded dataset ')
        dataset = Dataset.objects.filter(id=dataset_id).first()
        context['chosen_dataset'] = dataset
    
    if model and dataset:
        model_dataset = ModelDataset(model=model, dataset=dataset)
    
    model_dataset.save()

    if model_id:
        filtered_model_dataset_list = ModelDataset.objects.filter(model = model) 
        
        dataset_ids = filtered_model_dataset_list.values_list('dataset__id', flat=True)
        
        dataset_options = Dataset.objects.filter(id__in=dataset_ids)
        context['dataset_options'] = dataset_options

    return render(request, template_name, context=context)

def human_reinforced_feedback_view(request):
    template_name = "polls/human_reinforced_feedback.html"
    return render(request, template_name)

def final_task_analytics_view(request):
    template_name = "polls/final_task_analytics.html"
    return render(request, template_name)

def previous_tasks_view(request):
    template_name = "polls/previous_tasks.html"
    return render(request, template_name)

def personal_model_repo_view(request):
    template_name = "polls/personal_model_repo.html"
    return render(request, template_name)

def personal_dataset_analysis_view(request):
    template_name = "polls/personal_dataset_analysis.html"
    return render(request, template_name)