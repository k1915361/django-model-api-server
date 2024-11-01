from django import forms
from django.db.models import F
from django.http import HttpResponseRedirect
from .models import Dataset, Question, Choice
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template import Context, Template
from django.core.files.uploadhandler import MemoryFileUploadHandler, TemporaryFileUploadHandler
from django.core.files.storage import FileSystemStorage
import pprint
import sys
import os
import ast

ROOT_DATASET_DIR = 'asset/user/dataset/'

is_public_map_bool = {
    '1': False, '2': True, 
    1: False, 2: True,
    False: '1', True: '2',
}

is_public_map_label = {
    '1': 'private', '2': 'public', 
}

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]

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
    dataset = forms.FileField(required=False) # True
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

    model = forms.FileField()
    name = forms.CharField(max_length=320)
    model_type = forms.CharField(max_length=320)
    url = forms.CharField(max_length=2048, required=False)
    description = forms.CharField(max_length=320, required=False)
    is_public = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHOICES, 
    )

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
    if not request.user.is_authenticated:
        return login_message_view(request)

    return render(request, "polls/profile.html")

def register_view(request, context={}):
    template_name = "registration/register_view.html"
    return render(request, template_name, context)

def register_retry_view(request, context={'retry_register_message': 'Your username or email is already taken. Please try again.'}):
    return register_view(request, context)

def register(request):
    username = request.POST["username"]
    email = request.POST["email"]
    
    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        return redirect("/polls/register-retry-view/")
    
    password = request.POST["password"]

    user = User.objects.create_user(username, email, password)
    user.save()
    login(request, user)
    return redirect('/polls/logged-in/')

def login_view(request, context={}):
    template_name = "registration/login_view.html"
    return render(request, template_name, context)

def login_retry_view(request, context={'retry_login_message': 'Login was incorrect. Please try again.'}):
    return login_view(request, context)

def login_user(request):
    print("running login_user(request) ")
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None or request.user.is_authenticated:
        login(request, user)
        return redirect('/polls/logged-in/')
    
    return redirect('/polls/login-retry-view/')

def upload_model_view(request, context={}):
    template_name = "polls/upload_model.html"
    
    return render(request, template_name, context)

def upload_model(request):
    model = request.POST.get("model")
    model_file = request.FILES.get("model")
    modelname = request.POST.get("modelname")
    modeltype = request.POST.get("modeltype")
    modelurl = request.POST.get("modelurl")
    meta_description = request.POST.get("meta_description")
    description = request.POST.get("description")
    
    print("files", request.FILES)
    print("model file", model_file)
    print("modelname", modelname)
    print("modeltype", modeltype)
    print("model", model)
    print("modelurl", modelurl)
    print("meta_description", meta_description)
    print("description", description)

    return redirect("/polls/upload-model-view/")

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

def save_zip_file(zipfile, name, user, ispublic):
    save_dir = os.path.join(ROOT_DATASET_DIR, is_public_map_label[ispublic], str(user.id))
    timestamp = now_Ymd_HMS()
    save_filename = f'{timestamp}-{zipfile.name}'
    zipfile_dir = os.path.join(save_dir, save_filename)

    FileSystemStorage(location=save_dir).save(save_filename, zipfile) 
    dataset = Dataset(name=name, user=user, dataset_directory=zipfile_dir, is_public=is_public_map_bool[ispublic])
    dataset.save()
    return zipfile_dir, timestamp

def save_folder(files, directories, name, user, ispublic):
    home_directory = get_home_directory(directories.values())
    timestamp = now_Ymd_HMS()
    dataset_dir = os.path.join(ROOT_DATASET_DIR, is_public_map_label[ispublic], str(user.id), f"{timestamp}-{home_directory}")

    for file in files:
        relative_file_path = directories.get(file.name)
        relative_file_directory, _ = os.path.split(relative_file_path)
        
        file_dir = os.path.join(ROOT_DATASET_DIR, is_public_map_label[ispublic], str(user.id), f"{timestamp}-{relative_file_directory}")
        os.makedirs(file_dir, exist_ok=True)
        
        handle_uploaded_file(file, filename=file.name, dir=file_dir)

    dataset = Dataset(name=name, user=user, dataset_directory=dataset_dir, is_public=is_public_map_bool[ispublic])
    dataset.save()
    return

def upload_folder(request):
    if request.method != "POST":
        form = UploadDatasetForm()
        return render(request, "polls/upload_folder.html", {"form": form})
    
    form = UploadDatasetForm(request.POST, request.FILES)
    ispublic = request.POST.get("is_public")
    
    name = request.POST.get("name")
    directories_str = request.POST.get("directories")
    
    if directories_str:
        directories = ast.literal_eval(directories_str)

    zipfile_list = request.FILES.getlist('zipfile')

    if len(zipfile_list) != 0:
        zipfile = zipfile_list[0] 

        zipfile_dir, timestamp = save_zip_file(zipfile, name, request.user, ispublic)

        unzip_and_save(zipfile_dir, name, request.user, ispublic, timestamp)

    files = request.FILES.getlist('file')

    if form.is_valid() and len(files) != 0 and len(directories) != 0:
        save_folder(files, directories, name, request.user, ispublic)

    return render(request, "polls/upload_folder.html", {"form": form})

def upload_model(request):
    if request.method == "POST":
        print("upload_model() POST")
        form = UploadModelForm(request.POST, request.FILES)
                
        print("name - ", request.POST.get("name"))
        print("type - ", request.POST.get("type"))
        print("url - ", request.POST.get("url"))
        print("description - ", request.POST.get("description"))
        print("is_public - ", request.POST.get("is_public"))

        if form.is_valid(): 
            print("upload_model() POST form-is-valid") 
            handle_uploaded_file(request.FILES["file"], dir="asset/user/model/") 
    else:
        form = UploadModelForm()
    return render(request, "polls/upload_model.html", {"form": form})

def my_view(request):
    if not request.user.is_authenticated:
        """ 
        non-logged-in and non-registered guests:
        - can view public models and data
        - can upload and train models
        """        
        if "condition " == "data.is_private":
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")     

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