from django import forms
from django.db.models import F
from django.http import HttpResponseRedirect
from .models import Dataset, Model, Question, Choice
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
import sys
import os
import ast

ROOT_DATASET_DIR = 'asset/user/dataset/'
ROOT_MODEL_DIR = 'asset/user/model/'

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
    filepaths = forms.FilePathField(path=f"{ROOT_DATASET_DIR}public", recursive=True, allow_files=True, allow_folders=True, required=False)

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
            path=f"{ROOT_DATASET_DIR}public/{self.userid}",
            recursive=True,
            allow_files=True,
            allow_folders=True,
            required=False,
        )

        self.fields['filepaths_private'] = forms.FilePathField(
            path=f"{ROOT_DATASET_DIR}private/{self.userid}",
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
        return redirect('/polls/profile/')
    
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

def now_Ymd_HMS(format='%Y%m%d_%H%M%S'):
    return timezone.now().strftime(format)

def get_home_directory(directories):
    for directory in directories:
        for sep in ['/', '\\\\', '\\']:
            if sep in directory:
                return directory.split(sep)[0]
    return ''

def unzip_and_save(zipfile_dir, name, user, ispublic, timestamp):
    return

def save_zip_file(zipfile, name: str, user: User, ispublic: str):
    save_dir = os.path.join(ROOT_DATASET_DIR, is_public_map_label[ispublic], str(user.id))
    timestamp = now_Ymd_HMS()
    save_filename = f'{timestamp}-{zipfile.name}'
    zipfile_dir = os.path.join(save_dir, save_filename)

    FileSystemStorage(location=save_dir).save(save_filename, zipfile) 
    dataset = Dataset(name=name, user=user, dataset_directory=zipfile_dir, is_public=is_public_map_bool[ispublic])
    dataset.save()
    return zipfile_dir, timestamp

def save_model_folder_info_to_database(name: str, user: User, model_type: str, model_directory: str, ispublic: str, description: str = ""):
    model = Model(
        name=name, 
        user=user, 
        model_type=model_type, 
        model_directory=model_directory,
        description=description,
        is_public=is_public_map_bool[ispublic],
    )
    model.save()
    return

def save_dataset_folder_info_to_database(name: str, user: User, dataset_directory: str, ispublic: str):
    dataset = Dataset(
        name=name, 
        user=user, 
        dataset_directory=dataset_directory, 
        is_public=is_public_map_bool[ispublic],
    )
    dataset.save()
    return

def save_folder(files: list, directories: dict, user: User, ispublic: str, root_dir: str = ROOT_DATASET_DIR, name: str = ""):
    home_directory = get_home_directory(directories.values())
    timestamp = now_Ymd_HMS()
    dataset_dir = os.path.join(root_dir, is_public_map_label[ispublic], str(user.id), f"{timestamp}-{home_directory}")

    for file in files:
        relative_file_path = directories.get(file.name)
        relative_file_directory, _ = os.path.split(relative_file_path)
        
        file_dir = os.path.join(root_dir, is_public_map_label[ispublic], str(user.id), f"{timestamp}-{relative_file_directory}")
        os.makedirs(file_dir, exist_ok=True)
        
        handle_uploaded_file(file, filename=file.name, dir=file_dir)
    
    print(' - - - - ', ispublic, type(ispublic), is_public_map_bool[ispublic])
    return dataset_dir

def upload_folder(request):
    if request.method != "POST":
        form = UploadDatasetForm()
        return render(request, "polls/upload_folder.html", {"form": form})
    
    form = UploadDatasetForm(request.POST, request.FILES)
    ispublic = request.POST.get("is_public")
    
    name = request.POST.get("name")
    directories_str = request.POST.get("directories")
    
    if directories_str:
        directories_dict = ast.literal_eval(directories_str)

    zipfile_list = request.FILES.getlist('zipfile')

    if len(zipfile_list) != 0:
        zipfile = zipfile_list[0] 

        zipfile_dir, timestamp = save_zip_file(zipfile, name, request.user, ispublic)

        unzip_and_save(zipfile_dir, name, request.user, ispublic, timestamp)

    dataset_folder = request.FILES.getlist('file')

    if form.is_valid() and len(dataset_folder) != 0 and len(directories_dict) != 0:
        dataset_dir = save_folder(dataset_folder, directories_dict, request.user, ispublic, root_dir=ROOT_DATASET_DIR)
        save_dataset_folder_info_to_database(name, request.user, dataset_dir, ispublic)

    return render(request, "polls/upload_folder.html", {"form": form})

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
        model_directory = save_folder(model_folder, directories_dict, request.user, ispublic, root_dir=ROOT_MODEL_DIR)
        save_model_folder_info_to_database(name, request.user, model_type, model_directory, ispublic, description=description)
        
    return render(request, "polls/upload_model.html", {"form": form})

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
    template_name = "polls/process_model_options.html"
    return render(request, template_name)

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

def personal_dataset_repo_view(request):
    template_name = "polls/personal_dataset_repo.html"
    return render(request, template_name)

def personal_dataset_analysis_view(request):
    template_name = "polls/personal_dataset_analysis.html"
    return render(request, template_name)