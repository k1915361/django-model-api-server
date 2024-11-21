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
from pathlib import Path
import markdown
import json

def get_markdown_fenced_code(extensions=["fenced_code"]):
    return markdown.Markdown(extensions=extensions)

MARKDOWN_FENCED_CODE = get_markdown_fenced_code()

ROOT_DATASET_DIR = 'asset/user/dataset/'
ROOT_MODEL_DIR = 'asset/user/model/'
ROOT_TEMP = 'asset/temp/test'
TEXT_FILE_EXTENSIONS = {".txt", ".md", ".rst", ".html", ""}

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

def get_model__list(model, is_public: bool = True, order_by: str = "-created"):
    return model.objects.filter(is_public=is_public).order_by(order_by)

def get_model_list(model = Model, is_public: bool = True, order_by: str = "-created"):
    return get_model__list(model, is_public=is_public, order_by=order_by)

def get_dataset_list(model = Dataset, is_public: bool = True, order_by: str = "-created"):
    return get_model__list(model, is_public=is_public, order_by=order_by)

def get_user_model__list(model, user: User, is_public: bool = True, order_by: str = "-created"):
    return model.objects.filter(is_public=is_public, user=user).order_by(order_by)

def get_user_model_list(user: User, model = Model, is_public: bool = False, order_by: str = "-created"):
    return get_user_model__list(model, user, is_public=is_public, order_by=order_by)

def get_user_dataset_list(user: User, model = Dataset, is_public: bool = False, order_by: str = "-created"):
    return get_user_model__list(model, user, is_public=is_public, order_by=order_by)

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
    
    dataset_list = get_dataset_list()
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

    dataset_list = get_user_dataset_list(request.user)
    paginator = Paginator(dataset_list, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = { 'base_html': base_html, 'page_obj': page_obj }

    context['form'] = PrivateDatasetListPaginationView()
    return render(request, template_name, context)

def public_model_list_view(request, context={}):
    template_name = "polls/public_model_list_view.html"
    base_html = get_base_html(request.user.is_authenticated)
    
    model_list = get_model_list()
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

    model_list = get_user_model_list(request.user)
    paginator = Paginator(model_list, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = { 'base_html': base_html, 'page_obj': page_obj }

    context['form'] = PrivateModelListPaginationView()
    return render(request, template_name, context)

def index_homepage_view(request):
    template_name = "polls/index.html"
    base_html = get_base_html(request.user.is_authenticated)
    
    dataset_list = get_dataset_list()
    paginator = Paginator(dataset_list, 2)
    dataset_page_number = request.GET.get("dataset_page")
    dataset_page_obj = paginator.get_page(dataset_page_number)

    model_list = get_model_list()
    model_paginator = Paginator(model_list, 2)
    model_page_number = request.GET.get("model_page")
    model_page_obj = model_paginator.get_page(model_page_number)

    context = { 
        'base_html': base_html, 
        'dataset_page_obj': dataset_page_obj,
        'model_page_obj': model_page_obj,
    }

    if request.user.is_authenticated:
        private_dataset_list = get_user_dataset_list(request.user)
        context['dataset_private_page_obj'] = private_dataset_list

        private_model_list = get_user_model_list(request.user)
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
    public_model_list = get_model_list()
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

def iterate_folder(directory):
    """
    non-recursive root-only iteration.
    """
    for path in Path(directory).iterdir():
        yield path

def is_text_file(path):
    return path.suffix.lower() in TEXT_FILE_EXTENSIONS

def find_and_read_readme_text_file(directory: str):
    for path in iterate_folder(directory):
        if ("readme" in path.name.lower() 
            and path.is_file()
            and is_text_file(path)
        ):
            try:
                content = path.read_text(encoding='utf-8')
                return content
            except UnicodeDecodeError as e:
                print(f"`path.read_text(encoding='utf-8')`. Skipping non-text file: {path}. f{e}")
            try:
                content = path.read_text()
                return content
            except Exception as e:
                print(f"`path.read_text()`. Skipping non-text file: {path}. f{e}")
    return None

def search_and_get_readme_markdown_by_directory(directory):
    readme_text = find_and_read_readme_text_file(directory)
    readme_markdown = MARKDOWN_FENCED_CODE.convert(readme_text)
    return readme_markdown

def search_dataset_name(request, context: dict = {}) -> dict:
    models = []
    q = ""

    if request.method == "POST":
        q = request.POST.get("search-dataset-query")
        if q:
            models = Model.objects.filter(
                Q(name__icontains=q)
                & (Q(is_public=False
                     , user=request.user) 
                    | Q(is_public=True))
            )[:5]

    if not models:
        models = Model.objects.all()[:5]
    
    context = context | {
        "search_dataset_query_value": q, 
        "models": models
    }
    return context

def search_dataset_name_view(request, context: dict = {}, template_name: str = "polls/personal_dataset_repo.html"):
    context = search_dataset_name(request, context)    
    return render(request, template_name, context)

def read_dataset_info_json(directory: str, filename: str = "dataset_info.json"):
    file_path = os.path.join(ROOT_DATASET_DIR, directory or "1-20241107_192036-CS_dataset", filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get('type', None)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        print(f"Error: File content at {file_path} is not valid JSON")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return None

def personal_dataset_repo_view(request):
    if not request.user.is_authenticated:
        return redirect('/polls/login-view/')

    template_name = "polls/personal_dataset_repo.html"
    
    dataset_list = Dataset.objects.filter(
        Q(user=request.user)
        & (Q(is_public=False) 
           | Q(is_public=True
               , original_dataset__isnull=False))
    )

    context = { 
        'dataset_list': dataset_list,
    }

    POSTget = request.POST.get
    context['Nper_page'] = int(POSTget('Nper_page', 2))    
    context['chosen_dataset_id'] = POSTget('chosen_dataset_id')
    context['submit_dataset_id'] = POSTget('submit_dataset_id')
    context['upload_dataset'] = POSTget('upload_dataset')

    if context['submit_dataset_id'] != None:
        context['chosen_dataset_id'] = context['submit_dataset_id']

    context = list_pagination_v2(request, dataset_list, 'dataset_list', context) 

    if context['chosen_dataset_id'] != None and context['chosen_dataset_id'] != '':
        dataset = Dataset.objects.filter(id=context['chosen_dataset_id']).first()
        readme_markdown = search_and_get_readme_markdown_by_directory(dataset.dataset_directory)
        context['readme_markdown'] = readme_markdown

    if context['upload_dataset'] != None:
        return upload_folder(request, template_name, context)
        
    context = search_dataset_name(request, context)

    q = read_dataset_info_json('')
    print('read_dataset_info_json')
    print(q)

    return render(request, template_name, context)

def model_list_choose_one_to_relate_a_dataset(request):
    template_name = "polls/model_list_choose_one_to_relate_a_dataset.html" 
    public_model_list = get_model_list()
    context = {'public_model_list': public_model_list}

    if request.method != "POST":
        return render(request, template_name, context)
    
    chosen_model_id = request.POST.get('model_id')
    context['chosen_model_id'] = chosen_model_id
    context['chosen_model'] = Model.objects.filter(id=chosen_model_id).first()
    context['public_dataset_list'] = get_dataset_list()

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

def list_pagination_v2(request, list, namespace: str, context: dict):
    """
        namespace: eg. 'public_model_list', 'private_dataset_list'
    """    
    action = request.POST.get(f'{namespace}_page_action', '')
    context[f'{namespace}_page_num'] = int_(request.POST.get(f'{namespace}_page_num'), 0)
    Nper_page = context.get(f'{namespace}_Nper_page') or context.get('Nper_page', 2)

    if "first" in action:
        context[f'{namespace}_page_num'] = 0
        context[f'{namespace}_page_previous_disabled'] = 'disabled'
    if "previous" in action and context[f'{namespace}_page_num'] - Nper_page >= 0:
        context[f'{namespace}_page_num'] -= Nper_page
    if "previous" in action and context[f'{namespace}_page_num'] - Nper_page < 0:
        context[f'{namespace}_page_num'] = 0
    if "next" in action and context[f'{namespace}_page_num'] + Nper_page < len(list):
        context[f'{namespace}_page_num'] += Nper_page
    if context[f'{namespace}_page_num'] + Nper_page > len(list):
        context[f'{namespace}_page_num_end'] = len(list)        
    if "last" in action:
        context[f'{namespace}_page_num'] = len(list) - Nper_page
        context[f'{namespace}_page_next_disabled'] = 'disabled'
    if context[f'{namespace}_page_num'] - Nper_page > 0:
        context[f'{namespace}_page_previous_disabled'] = ''
    if context[f'{namespace}_page_num'] == 0:
        context[f'{namespace}_page_previous_disabled'] = 'disabled'
    if context[f'{namespace}_page_num'] + Nper_page < len(list):
        context[f'{namespace}_page_next_disabled'] = ''
    if context[f'{namespace}_page_num'] + Nper_page >= len(list):
        context[f'{namespace}_page_next_disabled'] = 'disabled'    
    if context.get(f'{namespace}_page_num_end') == None:
        context[f'{namespace}_page_num_end'] = context[f'{namespace}_page_num'] + Nper_page
    if context[f'{namespace}_page_num'] > len(list):
        context[f'{namespace}_page_num'] = len(list) - Nper_page
        context[f'{namespace}_page_num_end'] = len(list)

    context[f'{namespace}_to_view'] = list[context[f'{namespace}_page_num']: context[f'{namespace}_page_num_end']]

    return context

def list_pagination(model_list, action: str, page_no: int, Nper_page: int):
    previous_disabled = ''
    next_disabled = ''
    if "first" in action:
        page_no = 0 
        previous_disabled = 'disabled'
    if "previous" in action and page_no - Nper_page >= 0:
        page_no -= Nper_page 
    if "next" in action and page_no + Nper_page < len(model_list):
        page_no += Nper_page
    if "last" in action:
        page_no = len(model_list) - Nper_page
        next_disabled = 'disabled'

    if page_no - Nper_page > 0:
        previous_disabled = ''
    if page_no == 0:
        previous_disabled = 'disabled'

    if page_no + Nper_page < len(model_list):
        next_disabled = ''
    if page_no + Nper_page >= len(model_list):
        next_disabled = 'disabled'

    return (page_no, 
            model_list[page_no: page_no + Nper_page], 
            previous_disabled, 
            next_disabled)

def save_model_to_file_system_and_database(user: User, uploaded_model, model_directories_str: str, model_name: str, model_type: str, model_ispublic: str, timestamp: datetime):
    if len(uploaded_model) != 0 and model_directories_str != None and len(model_directories_str) != 0 and model_directories_str != "":
        model_directories_dict = ast.literal_eval(model_directories_str)
        
    if len(uploaded_model) != 0 and len(model_directories_dict) != 0 and model_name and model_type and model_ispublic: 
        model_directory = save_folder(
            uploaded_model, 
            model_directories_dict, 
            user, 
            timestamp, 
            root_dir=ROOT_MODEL_DIR
        )
        model = save_model_folder_info_to_database(
            model_name, 
            user, 
            model_type, 
            model_directory, 
            model_ispublic
        )
        return model

def save_dataset_to_file_system_and_database(user: User, uploaded_dataset, dataset_directories_str: str, dataset_name: str, dataset_ispublic: str, timestamp: datetime):
    if len(uploaded_dataset) != 0 and dataset_directories_str != None and len(dataset_directories_str) != 0 and dataset_directories_str != "":
        dataset_directories_dict = ast.literal_eval(dataset_directories_str)
        
    if len(uploaded_dataset) != 0 and len(dataset_directories_dict) != 0 and dataset_name and dataset_ispublic:
        dataset_directory = save_folder(
            uploaded_dataset, 
            dataset_directories_dict, 
            user, 
            timestamp, 
            root_dir=ROOT_DATASET_DIR
        )
        dataset = save_dataset_folder_info_to_database(
            dataset_name, 
            user, 
            dataset_directory, 
            dataset_ispublic
        )
        return dataset

def set_chosen_model(model: Model, uploaded_model, chosen_model_id, context: dict):
    if model == None and len(uploaded_model) == 0 and type(chosen_model_id) == int:
        model = Model.objects.filter(id=chosen_model_id).first()
        context['chosen_model'] = model
        context['chosen_model_id'] = model.id
        return model, context
    return model, context

def set_chosen_dataset(dataset: Dataset, uploaded_dataset, chosen_dataset_id, context: dict):
    if dataset == None and len(uploaded_dataset) == 0 and type(chosen_dataset_id) == int:
        dataset = Dataset.objects.filter(id=chosen_dataset_id).first()
        context['chosen_dataset'] = dataset
        context['chosen_dataset_id'] = dataset.id
    return dataset, context

def save_model_dataset(model: Model, dataset: Dataset, context: dict):
    if model and dataset:
        model_dataset = ModelDataset(model=model, dataset=dataset)
        found_model_dataset = ModelDataset.objects.filter(model=model, dataset=dataset)
        if found_model_dataset == None:
            model_dataset.save()
            context["ModelDataset_creation_success_message"] = 'Successfully created ModelDataset association.'
        if found_model_dataset != None:
            context["ModelDataset_creation_success_message"] = 'ModelDataset association already exists.'
        return model_dataset, context
    return None, context

def set_model_dataset_options(chosen_model_id, model: Model, context: dict):
    if type(chosen_model_id) == int:
        filtered_model_dataset_list = ModelDataset.objects.filter(model = model) 
        
        dataset_ids = filtered_model_dataset_list.values_list('dataset__id', flat=True)
        
        model_dataset_options = Dataset.objects.filter(id__in=dataset_ids)
        context['model_dataset_options'] = model_dataset_options

        if len(model_dataset_options) == 0:
            context['model_datasets_not_found'] = True
        return model_dataset_options, context
    return [], context

def int_(str, default_val = None):
    if str != 'None' and str != None and str != '':
        return int(str)
    if (str == 'None' or str == None or str == '') and default_val != None:
        return default_val
    return str
    
def process_model_options_view(request):
    if not request.user.is_authenticated:
        return redirect('/polls/login-view/')
    
    template_name = "polls/process_model_options.html"
    dataset_list = get_dataset_list()
    model_list = get_model_list()
    private_dataset_list = get_user_dataset_list(request.user)
    private_model_list = get_user_model_list(request.user)
    model_dataset_options = []

    context = {
        "public_model_list": model_list,
        "public_dataset_list": dataset_list,
        'private_model_list': private_model_list,
        'private_dataset_list': private_dataset_list,
        "public_model_list_length": len(model_list),
        "public_dataset_list_length": len(dataset_list),
    }

    POSTget = request.POST.get
    FILESget = request.FILES.getlist
    context['Nper_page'] = int(POSTget('Nper_page', 2))
    Nper_page = context['Nper_page']
    timestamp = now_Ymd_HMS()

    model = None
    chosen_model_id = int_(POSTget("chosen_model_id"))
    model_name = POSTget("model_name")
    model_type = POSTget("model_type")
    model_ispublic = POSTget("model_is_public")
    model_directories_str = POSTget("model_folder_directories")
    uploaded_model = FILESget("form_model_folder")    
    model_page_action = POSTget('model_page_action', '')
    model_page_num = int_(POSTget("model_page_num"), 0)
    
    dataset = None
    chosen_dataset_id = int_(POSTget("chosen_dataset_id"))
    dataset_name = POSTget("dataset_name")
    dataset_ispublic = POSTget("dataset_is_public")
    dataset_directories_str = POSTget("dataset_folder_directories")
    uploaded_dataset = FILESget("form_dataset_folder")
    dataset_page_action = POSTget('dataset_page_action', '')
    dataset_page_num = int_(POSTget("dataset_page_num"), 0)
    
    private_model_page_action = POSTget('private_model_page_action', '')
    private_model_page_num = int_(POSTget("private_model_page_num"), 0)
    
    private_dataset_page_action = POSTget('private_dataset_page_action', '')
    private_dataset_page_num = int_(POSTget("private_dataset_page_num"), 0)
    
    model_dataset_page_action = POSTget('model_dataset_page_action', '')
    model_dataset_page_num = int_(POSTget("model_dataset_page_num"), 0)
   
    unselect_model_option = POSTget("unselect_model_option")
    unselect_dataset_option = POSTget("unselect_dataset_option")

    start_process_action = POSTget("start_process_action")
    choose_model_action = POSTget("choose_model_action")
    
    if unselect_model_option != None: chosen_model_id = None
    if unselect_dataset_option != None: chosen_dataset_id = None
    
    (context['model_page_num'], 
    context['public_model_list'],
    context['public_model_page_previous_disabled'],
    context['public_model_page_next_disabled']) = list_pagination(model_list, model_page_action, model_page_num, Nper_page) 
    
    (context['dataset_page_num'], 
    context['public_dataset_list'],
    context['public_dataset_page_previous_disabled'],
    context['public_dataset_page_next_disabled']) = list_pagination(dataset_list, dataset_page_action, dataset_page_num, Nper_page)
    
    (context['private_model_page_num'], 
    context['private_model_list'],
    context['private_model_page_previous_disabled'],
    context['private_model_page_next_disabled']) = list_pagination(private_model_list, private_model_page_action, private_model_page_num, Nper_page)

    (context['private_dataset_page_num'], 
    context['private_dataset_list'],
    context['private_dataset_page_previous_disabled'],
    context['private_dataset_page_next_disabled']) = list_pagination(private_dataset_list, private_dataset_page_action, private_dataset_page_num, Nper_page)
    
    if start_process_action == 'start_process_action' or choose_model_action == 'choose_model_action':
        model = save_model_to_file_system_and_database(request.user, uploaded_model, model_directories_str, model_name, model_type, model_ispublic, timestamp)

        dataset = save_dataset_to_file_system_and_database(request.user, uploaded_dataset, dataset_directories_str, dataset_name, dataset_ispublic, timestamp)

    model, context = set_chosen_model(model, uploaded_model, chosen_model_id, context)

    dataset, context = set_chosen_dataset(dataset, uploaded_dataset, chosen_dataset_id, context)
    
    if start_process_action == 'start_process_action' or choose_model_action == 'choose_model_action':
        _, context = save_model_dataset(model, dataset, context)
    
    _, context = set_model_dataset_options(chosen_model_id, model, context) 
    
    (context['model_dataset_page_num'], 
    context['model_dataset_list'],
    context['model_dataset_page_previous_disabled'],
    context['model_dataset_page_next_disabled']) = list_pagination(model_dataset_options, model_dataset_page_action, model_dataset_page_num, Nper_page)

    context = {
        "chosen_model_id": chosen_model_id,
        "chosen_dataset_id": chosen_dataset_id,
        **context
    }
    
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