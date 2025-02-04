# django-model-api-server

This API server is developed with the Frontend application:  
<https://github.com/k1915361/2024-Nov-frontend-nextjs>

## Setting up PostgreSQL

```sh
# locate pip
which pip
/home/user/my_env/bin/pip

# list all pips in location learned above
ls /home/user/my_env/bin/pip*

# list all pips in user directory outside of virtual environment
ls /usr/bin/pip*

pip -V
# pip 24.0 from /home/user/my_env/lib/python3.12/site-packages/pip (python 3.12)

python3.11 -m pip install dotenv 

# if not resolved try:
# python3.11 -m pip install python-dotenv

# check outdated wheel and setuptools and upgrade
python3.11 -m pip uninstall psycopg2
python3.11 -m pip list --outdated 
python3.11 -m pip install --upgrade wheel
python3.11 -m pip install --upgrade setuptools

# important step before pip install
sudo apt install libpq-dev

# resolving error: command '/usr/bin/x86_64-linux-gnu-gcc' failed with exit code 1
sudo apt-get install python3.11-dev

python3.11 -m pip install psycopg2

python3.11 -m pip list 
python3.11 -m pip list | grep psy

sudo apt install postgresql

# Go to file
code /etc/postgresql/16/main/postgresql.conf

# Change the address to '*'
# listen_addresses = 'localhost'
# listen_addresses = '*'
# Note: '*' will allow all available IP interfaces (IPv4 and IPv6), to only listen for IPv4 set 0.0.0.0 while '::' allows listening for all IPv6 addresses.

sudo -u postgres psql template1
ALTER USER postgres with encrypted password 'ku202425';
# ctrl + z  to exit

# edit file to use scram-sha-256 authentication with the postgres user
# hostssl template1       postgres        192.168.122.1/24        scram-sha-256
sudo echo 'hostssl template1       postgres        192.168.122.1/24        scram-sha-256' | sudo tee -a /etc/postgresql/16/main/pg_hba.conf

sudo systemctl restart postgresql.service

whereis python3.11
# /usr/bin/python3.11

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 20

sudo update-alternatives --config python
# Press <enter> to keep the current choice[*], or type selection number: 0

python -V

source ~/.bashrc

export DJANGO_SETTINGS_MODULE=ku_djangoo.settings
```

## Making migrations to database

https://docs.djangoproject.com/en/5.1/intro/tutorial02/

```sh
python manage.py makemigrations polls
# or
python3.11 -m manage makemigrations polls

python manage.py sqlmigrate polls 0004
python manage.py sqlmigrate polls 0005
python manage.py sqlmigrate polls 0006
python manage.py sqlmigrate polls 0007
python manage.py sqlmigrate polls 0008
python manage.py sqlmigrate polls 0009
python manage.py sqlmigrate polls 0010
python manage.py sqlmigrate polls 0011
python manage.py sqlmigrate polls 0012
python manage.py sqlmigrate polls 0013
python3.11 -m manage sqlmigrate polls 0014
python3.11 -m manage sqlmigrate polls 0015
python3.11 -m manage sqlmigrate polls 0016
python3.11 -m manage sqlmigrate polls 0017
python3.11 -m manage sqlmigrate polls 0018
python3.11 -m manage sqlmigrate polls 0019
python3.11 -m manage sqlmigrate polls 0020

python manage.py migrate
# or
python3.11 -m manage migrate
```

# Resolving: "could not create unique index"

```bash
$ python3.11 -m manage migrate
...
django.db.utils.IntegrityError: could not create unique index "unique_dataset_name_user"
DETAIL:  Key (name, user_id)=(CS dataset, 1) is duplicated.
```

`python3.11 -m manage runserver` run this command and go to admin page `http://localhost:8000/admin/polls/dataset/`, rename `name` of dataset for unique names to avoid duplicates. As a second option, delete records with duplicate names. Then run the `migrate` command again and start server application as it is normally done.

## Creating an admin or superuser

```sh
python manage.py createsuperuser

# Username: admin
# Email address: admin@example.com

# Password: apassword
# Password (again): apassword
# Superuser created successfully.

# python manage.py runserver
python3.11 -m manage runserver
```

## Creating first login database record

```sh
python manage.py shell

from polls.models import User

User.objects.all()

u = User(email="ace@email.com", password="apassword", username="ace")
u.save()
u.id
u.email
u.password
u.username

User.objects.all()

# ctrl + z  to exit python shell
```

## Updating user database record

```sh
python manage.py shell

from polls.models import User

User.objects.all()

u = User.objects.filter(username="ace")[0]
u.password
u.set_password("new password")
u.password

u.save()

# ctrl + z  to exit python shell
```

## Creating first model database record

```sh
# python manage.py shell

from polls.models import Net_Model, Login

Net_Model.objects.all()

l = Login.objects.get(pk=1)

n = Net_Model(name="aceNet", model_type="aceNetType", owner_id=l, meta_description="aceNet meta description", model_url="example.com", description="ace-net description")

n.save()

n.name
n.meta_description
n.model_url

Net_Model.objects.all()
```

## Testing

```sh
python manage.py test polls

# output messsage
Found 10 test(s).
Creating test database for alias 'default'...
Got an error creating the test database: source database "template1" is being accessed by other users
DETAIL:  There are 5 other sessions using the database.
```

## Does Django close database connection?

Django closes the connection once it exceeds the maximum age defined by CONN_MAX_AGE or when it isn't usable any longer.

[Databases | Django documentation](https://docs.djangoproject.com/en/5.1/ref/databases/)

## Clearing Django cache

```sh
# python manage.py shell

from django.db import connections, transaction
from django.core.cache import cache # This is the memcache cache.

cache.clear()
```

## Designing Web Layout

Forms
https://getbootstrap.com/docs/5.3/forms/input-group/#basic-example

## Making HTML Templates

Template  
https://docs.djangoproject.com/en/5.1/ref/templates/language/


## Deleting all data in database tables

```sh
python manage.py flush
```

## Resolving 'polls' is not a registered namespace

> "django.urls.exceptions.NoReverseMatch: 'polls' is not a registered namespace"

At main application folder where `settings.py`, `asgi.py`, `wsgi.py` files are:  
Ensure to add `namespace='polls'`.  
Ensure to match the application folder name `polls`.

`ku_djangoo/urls.py`

```py
urlpatterns = [
    path('polls/', include('polls.urls', namespace='polls')),
    ...
]
```

Ensure correct spellings such as `app_name`, check wrong spellings such as `app_names`.  

`polls/urls.py`

```py
app_name = 'polls'
```

`manage.py`

```py
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ku_djangoo.settings')
```

`settings.py`

```py
ROOT_URLCONF = 'ku_djangoo.urls' 
```
## Saving Python Packages and versions

```sh
pip freeze > requirements.txt
python3.11 -m pip freeze > requirements_python_3_11.txt
```

## Hiding Sidebar at mobile screen

Bootstrap
Layout Breakpoints

| Breakpoint | Class infix | Dimensions |
| - | - | - |
| Extra small | None |  <576px |
| Small | sm | ≥576px |
| Medium | md | ≥768px |
| Large | lg | ≥992px |
| Extra large | xl | ≥1200px |
| Extra extra large | xxl |  ≥1400px |

Bootstrap - Utilities - Display  

Hidden on all  
`d-none`

Hidden only on sm - for tablet and desktop side navigation bar  
`d-none d-sm-inline`

Visible only on xs - for mobile top navigation bar  
`d-block d-sm-none`

Visible only on sm - for tablet-mobile top navigation bar  
`d-none d-sm-inline d-md-none`  

Choose either `-inline` or `-block`.

## Finding history of commands

```sh
ctrl + r

# search for your past command 
cd 
# (reverse-i-search)`cd': cd ~/Documents/ku_django/

# enter if the result command is what you are looking for
```

## Finding python package version

```sh
pip list | grep Dj
# Django 4.2.11

pip --version
# pip 24.0 from /usr/lib/python3/dist-packages/pip (python 3.12)
```

## Generating sample templates with DJango form

`polls/views.py`
```py
from django import forms

class AForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

def aview(request):
    if request.method == "POST":
        form = AForm(request.POST, request.FILES)
    else:
        form = AForm()
    return render(request, "polls/aview.html", {"form": form})
```

`polls/templates/polls/aview.html`
```html
{% for field in form %}
    <div class="fieldWrapper ">
        {{ field.errors }}
        <label for='{{ field.label_tag }}' >
            {{ field.label_tag }}
        </label>
        <div class="" id='{{ field.label_tag }}'>
            {{ field }}
        </div>
    </div>
{% endfor %}
```

## Saving an Uploaded Folder and Zip File to a Directory

Current implementation is seen at `polls/views.py` at function `upload_folder(request)` under the line `for file in files:`.

Below are helpful resources and options to help achieve or improve the implementation. 

Option 1  
`polls/models.py`  
<https://stackoverflow.com/questions/65588269/how-can-i-create-an-upload-to-folder-that-is-named-a-field-belonging-to-the-mode>  
```py
class Upload(models.Model):
    def user_directory_path(instance, filename):        
        return 'user_{0}/{1}'.format(instance.user.id, filename) # uploaded to MEDIA_ROOT/user_<id>/<filename>
```

Option 2  
<https://forum.djangoproject.com/t/how-to-zip-files/17197/1>  
```py
class Upload(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def save_folder(instance, filename):
        upload_to = ''
        ext = filename.split('.')[-1]
        filename = '{}_{}.{}'.format('classA', instance.uuid, ext)
        return os.path.join(upload_to, filename)
    folder = models.FileField(upload_to=save_folder, null = True , blank = True )
```
    
Option 3.1  
Upload image instead of folder using `models` and `.Field(upload_to=)` with eg. `%Y/%m/%d`, `foldername`, `fn_upload`.  
<https://bdvade.hashnode.dev/structuring-file-uploads-in-django>  
```py
from django.template.defaultfilters import slugify

def category_upload(instance, filename):
    return f"categories/{slugify(instance.category.name)}/{slugify(instance.name)}/{slugify(filename)}"

class Article(models.Model):
    name = models.CharField(max_length=30)
    body = models.CharField(max_length=5000)
    image = models.ImageField(upload_to=category_upload)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # 
    # categories/web-development/intro-to-web-development/cover.jpg
```

Option 3.2
```py
class Article(models.Model):
    ...
    image = models.ImageField(upload_to='%Y/%m/%d')
    # 
    # 2018/06/12/cover.jpg

```

Option 3.3  
```py
class Article(models.Model):
    ...
    image = models.ImageField(upload_to='article')
    # 
    # article/cover.jpg
```

Option 4
Uploading folder structure directories along with the folder
<https://diginaga.online/django/python/code/2019/04/10/directory_upload_django.html>

```html
<form method='POST' enctype="multipart/form-data">
    <input type="file" id="file_input" name="file_field" webkitdirectory directory/>
    <input type="text" id="directories" name="directories" hidden />
    <input type="submit"/>
</form>
<script>
    files = document.querySelector("#file_input").files;
    document.querySelector("#file_input").addEventListener("change", function() {
        files = document.querySelector("#file_input").files;
        var directories = {}
        for (var file of files) {
            file.webkitRelativePath
            directories[file.name] = file.webkitRelativePath
        }
        directories = JSON.stringify(directories);
        document.querySelector("#directories").value = directories
    });
</script>
```

This fourth method however, for some reason, the directories are not properly being received on the server side.  
The root issue is unknown yet.

The issue was found. 

1. There were two duplicate hidden input for storing directories.
2. Second possible issue is that the location of the JavaScript was placed outside of a 'div' document container, whereas it should be placed right under the form document - under where the `</form>` ends. 

Option 5  
Uploading Zip file and save as is.  
<https://stackoverflow.com/questions/74300563/save-uploaded-inmemoryuploadedfile-as-tempfile-to-disk-in-django>  

`polls/templates/polls/upload_folder.html`
```html
<label for="id_zipfile" class="form-label">Zip File:</label>
<input type="file" accept=".zip,.rar,.7zip" name="zipfile" id="id_zipfile" class="form-control mb-1">
<input type="text" id="directories" name="directories" hidden/>
```

`/home/user/Documents/ku_django/polls/views.py`
```py
from django.core.files.storage import FileSystemStorage

def simple_view(request):
    in_memory_file_obj = request.FILES["file"]
    FileSystemStorage(location="/tmp").save(in_memory_file_obj.name, in_memory_file_obj)
```

This method is tested and working, but, the zip format would not allow users to view the dataset content.  
Therefore unzipping this file and saving as a folder is necessary.
The data type is not a File or ZipFile but DJango's `TemporaryUploadedFile` with methods from `UploadedFile`, read the documentation.

## What is the advantage of ASGI vs WSGI?

ASGI's async does not speed up the throughput of CPU-bound processes. 

ASGI asynchronises and reduces waiting time for I/O: 
- to local or remote Database, 
- third party API calls, 
- exporting storage to another storage, 
- database to S3 static file blobs, 
- multiple network requests, 
- parallel API calls, 
- parallel upload/download, 
- streaming/broadcasting videos, etc.
- async view (HTML rendering) and async I/O

<https://forum.djangoproject.com/t/what-does-switching-to-asgi-entail/26857/3>

## Installing Django 

```sh
sudo apt update
sudo apt install python3-django

python -m pip list | grep ja
# Django 5.1.2

python -m django --version
# 5.1.2

django-admin --version
# 5.1.2

sudo apt update
python3 -V
# 3.12.3

sudo apt-get update
sudo apt install python3-pip python3-venv
sudo apt install python3-dev

# for python3.11
# sudo apt-get install python3.11-dev
# sudo apt install python3.11-venv

# check pip version
python3 -m pip --version
# pip 24.0 from /home/user/my_env/lib/python3.12/site-packages/pip (python 3.12)

# check current env
python
import sys
print(sys.prefix)
# /home/user/my_env

# ctrl + z to exit
# /usr

pip install django

# A Guide from Writing your first Django app. https://docs.djangoproject.com/en/5.1/intro/tutorial01/

# create a project
django-admin startproject ku_django
cd ku_django/

# initial migration for sessions and contenttypes
python manage.py migrate

# python manage.py runserver
python3.11 -m manage runserver
```

Throughout the whole document, the project aimed to use python 3.11 for stability, however development troubles were encountered. 
Use 3.12 or 3.11 based on your preferrence.  
In practise use `python` or `python3.12 -m` instaed of `python3.11 -m`.  

## Making a Python environment

```sh
python -V
# 3.12.3
python3 -V
# 3.12.3

python -m pip --version
# pip 24.0 from /home/user/my_env/lib/python3.12/site-packages/pip (python 3.12)
python3 -m pip --version
# same output

cd /home/user/

# make env
python3 -m venv my_env
# Python 3.12

mkdir /home/user/Documents/ku_django/
cd /home/user/Documents/ku_django/

# activate 
source /home/user/my_env/bin/activate

# optional deactivate
deactivate
```

## Making a beginner sample application

```sh
cd /home/user/Documents/ku_djangoo/
python manage.py startapp polls
```

## Saving dataset into file system and database

Old file system folder structure:
```
ku_django
- asset
 - user
  - dataset
   - private
   - public
    - <user_id>
     - <timestamp>-<original_folder_name>
    - 1
    - 2
  - model
   - private
   - public
```

What if user wants to switch public/private state?  
It is inefficient moving the dataset compared to simply switching "is_public" boolean field in the database (or "public"/"private" string in the file name).

New file system folder structure:
```
- asset
 - user
  - dataset
   - <user_id>-<timestamp>-<original_folder_name>
   - 1-20001010_101010-A_dataset
  - model
   - <user_id>-<timestamp>-<original_folder_name>
   - 2-20001010_101010-A_model
```

It is not necessary to include the user-ID in the folder name.  

However, in this project, it was considered that folders with same name maybe uploaded at the same time (though chance is nearly none, it is not impossible),  

This will cause problem where a user will be directed to the wrong folder with the right directory path saved in the database. 

If that dataset is private it would be a privacy issue and potentially a information property breach and misuse, exploitation of this bug or design defect.  

## Allowing guest without account to upload models and datasets 

Currently it is allowed, in the future this decision may change in this project.

`polls/models.py`
```python
    class Model(models.Model):
        user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
```

## Formatting human readable datetimes

Format:  

30 seconds ago  
30 minutes ago  
3 hours ago  
2 days ago  
dd Mmm  
01 Jan  
dd Mmm yyyy  
01 Jan 2000  

option 1.  
`polls/test/test.py` and  
`polls/views.py`  
```py
def timestamp_humanize(timestamp: datetime) -> str:
    now = dt.now()
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

def example_view(request):
    dataset = Dataset.objects.filter(is_public=False, user=request.user).annotate(
        updated_str = F('updated')
    ).order_by("-created")
    
    for dtst in dataset:
        dtst.updated_str = timestamp_humanize(dtst.updated_str)
```

`polls/templates/polls/personal_dataset_repo.html`  
```html
• {{ dataset.updated_str }} ago
```

Use command `python polls/test/test.py ` to do assert tests.

option 2.  

`polls/templatetags/custom_filters.py`  
```py
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def upto(value, delimiter=','):
    return value.split(delimiter)[0]
upto.is_safe = True
```

`polls/templates/polls/personal_dataset_repo.html`  
```html
{% load custom_filters %}
• {{ dataset.updated|timesince|upto:',' }} ago
```

`','` parameter is optional and can be eliminated.

option 3.

`ku_django/ku_djangoo/settings.py`  
```py
INSTALLED_APPS = [
    'django.contrib.humanize',
]
```

`polls/templates/polls/personal_dataset_repo.html`  
```html
{% load humanize %}
• {{ dataset.updated|naturaltime }}
```

## Accessing list of hidden development links

addresses starting with `http://localhost:8000/polls/`:
`upload-model/`
`upload-folder/`
`public-model-list-view/`  
`public-dataset-list-view/`
`dataset-list-view-to-fork/`  
`private-model-list-view/`
`private-dataset-list-view/`
`user_dataset_list_path_view/`
`model-list-choose-one-to-relate-dataset/`

## Choosing On delete database options

Choosing not to delete or "cascade" has an advantage of preserving data of how many times the model or dataset are in relationship, this may give some insight into their popularity. The disadvantage is the issues of non-existing objects where None objects and values must be handled. Otherwise, filter must be implemented to prevent fetching rows with deleted referenced objects when rendering webpages.

`polls/models`
```py
class ModelDataset(models.Model):
    model = models.ForeignKey(Model, on_delete=models.DO_NOTHING) 
    dataset = models.ForeignKey(Dataset, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(default=timezone.now) 
```

## Preserving form data while navigating pages

<https://stackoverflow.com/questions/71443933/paginator-and-post-request-for-searchform>

```py
def order_list(request):
    ...
    get_data = request.GET.copy()
    page = get_data.pop('page', None)
    ...

    context = {
        ...,
        'query_string': get_data.urlencode(),
     }
    return render(request, 'order/list.html', context)
```

Template
```html
    <a href="?{% if query_string %}{{ query_string }}&{% endif %}page={{ page_obj.next_page_number }}">next</a>
```

## Implementing Live search

<https://www.circumeo.io/blog/entry/build-a-live-search-feature-with-django-using-htmx-and-postgresql-fts-in-10-minutes/>

This page shows implementation of Search Vector Field Django's `SearchQuery`.

This project Implements simple `name` search with `icontains` (case-insensitive `i`) at the time of writing this section.

<https://docs.djangoproject.com/en/5.1/ref/contrib/postgres/lookups/#std-fieldlookup-trigram_similar>

This page shows other options for searching: 

`__trigram_similar`: Middlesborough ~ Middlesbrough

`__trigram_word_similar`: Middlesborough ~ Middlesbrough

`__unaccent`: México ~ Mexico.

<https://docs.djangoproject.com/en/5.1/ref/models/querysets/>

`__in`: eg. `blog__name__in=names`. search items that matches one item from a list.

`__endswith`: eg. `headline__endswith="Lennon"`.

`__range`: `pub_date__range=(start_date, end_date)`

`gte`: Greater than or equal to.  
`lt`: Less than.  
`lte`: Less than or equal to.  
`startswith`  
`endswith`  

`pub_date__iso_year__gte=2005`

Implementation of live search can be seen at template file `polls/templates/polls/personal_dataset_repo.html` below the line `Optional - Link a model to a chosen dataset:` and `polls/views.py` at function named `personal_dataset_repo_view` or `search_dataset_name`.

note that the function and view-function is seperated `search_dataset_name` and `search_dataset_name_view`. 

State management:  
(1) the function adds items to `context`,  
(2) temporarily stores values (id, page_no., etc.) into html `input`s (`hidden` or visible),  
(3) the function brings back the values with `request.POST.get` and then feeds back to the `context`.  

This enables temporarily storing user actions, options, page navigations (of multiple paginated lists), chosen item IDs, and multiple values (int, string, and possibly binary). 

Only non-sensitive data is stored in the HTML content at the client side. 

This approach do not require caching or `session` caching at server side. 

## Ensuring Token Table is Created

Ensure that the authtoken app is listed in your INSTALLED_APPS:

```py
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'rest_framework.authtoken',
]
```

Run migrations to create the table:

```sh
python manage.py migrate
```

In the Django Administrator page `http://localhost/admin/auth/user/`, the Token table will be seen under `AUTH TOKEN`.

## Testing API

```bash
curl -u admin -H 'Accept: application/json; indent=4' http://127.0.0.1:8000/users/
Enter host password for user 'admin':
``` 

Or directly through the browser, by going to the URL `http://127.0.0.1:8000/users/...`

## Testing API Post (Put/Create)

```bash
http --form POST http://127.0.0.1:8000/polls/models_/ name="test model G" is_public="true" model_type="test type G"
```

```bash
http POST http://127.0.0.1:8000/polls/models_/ name="test model G" is_public="true" model_type="test type G"

{
    "detail": "Authentication credentials were not provided."
}

```

```bash
http -a admin:password123 POST http://127.0.0.1:8000/polls/models_/ name="test model G" is_public="true" model_type="test type G"
```

Download a dataset zip file.

```bash
curl \
  -X GET http://localhost:8000/api/dataset/download/test/ \
  -o dataset.zip
```

## Fetching Model's Creator Username using Serializers

```py
class ModelSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Model
        fields = ["id", "name", "updated", "is_public", "original_model", "username"]
```

## Installing Django cors headers

`python3.11 -m pip install django-cors-headers`

## Setting up JWT token

<https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html>

```sh
python3.11 -m pip install cffi
python3.11 -m pip install djangorestframework-simplejwt
python3.11 -m pip install djangorestframework-simplejwt[crypto]
```

`settings.py`
```py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt', 
    ...
]

REST_FRAMEWORK = {
    ...
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # Default permissions
    ),
    ...
}
```

`urls.py`
```py
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenVerifyView
)

urlpatterns = [
    ...
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
```

Usage and verify

```sh
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "adminpass"}' \
  http://127.0.0.1:8000/api/token/

# return output
{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMjg5NzU5OCwiaWF0IjoxNzMyODExMTk4LCJqdGkiOiI4MzRhZTA3MzRlZTE0MGZkOTQ3YjAyOTM0NzFmMDJlZiIsInVzZXJfaWQiOjF9.NEmbsXNgft0rUalS4UT2yUz4Xa4I5y5FSWnFoClmAAI","access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyODExNDk4LCJpYXQiOjE3MzI4MTExOTgsImp0aSI6IjE3MzNlMThhOGMwMzRhOGRhMzE2OWVmNzM0ZTU4MTg5IiwidXNlcl9pZCI6MX0.XwV95FYBn2WNUKtPExzL8dnJ8A9E__Rs7UGrNmNhgOo"}
```

```sh

# from "access" token
curl \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyODExNDk4LCJpYXQiOjE3MzI4MTExOTgsImp0aSI6IjE3MzNlMThhOGMwMzRhOGRhMzE2OWVmNzM0ZTU4MTg5IiwidXNlcl9pZCI6MX0.XwV95FYBn2WNUKtPExzL8dnJ8A9E__Rs7UGrNmNhgOo" \
  http://127.0.0.1:8000/api/token/verify/protected-data/
```

When this short-lived access token expires, you can use the longer-lived refresh token to obtain another access token:

```sh
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMjg5NzU5OCwiaWF0IjoxNzMyODExMTk4LCJqdGkiOiI4MzRhZTA3MzRlZTE0MGZkOTQ3YjAyOTM0NzFmMDJlZiIsInVzZXJfaWQiOjF9.NEmbsXNgft0rUalS4UT2yUz4Xa4I5y5FSWnFoClmAAI"}' \
  http://localhost:8000/api/token/refresh/

# return output
{"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyODEyMTk5LCJpYXQiOjE3MzI4MTExOTgsImp0aSI6IjIxNjEwMzdmMmM5ZjRmOWI4Yzc2MDgyNTM2ODhlN2EwIiwidXNlcl9pZCI6MX0.sviz9yVyViSO_Sz7LU91nt-j1tBszBwj6bDlXgPDkfc"}


```

`polls/api.py`
```py
class CustomLoginTokenAccessView(APIView):
    ...
    def post(self, request, *args, **kwargs):
        ...
        response.set_cookie(
            "access_token", access_token, httponly=True, secure=False
        )
```

Only set `secure` to `True` when using HTTPS (not HTTP) hosting.

Testing `CustomTokenRefreshView` and `CustomLoginTokenAccessView`

```sh
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -b cookie.txt -c cookie.txt \
  -d '{"username": "admin", "password": "adminpass"}' \
  http://localhost:8000/api/token/login/cookie/
  
# -c cookie.txt: Save cookies to a file 

# return output
{"success": true, "username": "admin"}
# and cookie.txt created/updated in current directory

# 
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -v -b cookie.txt -c cookie.txt \
  -d '{}' \  
  http://localhost:8000/api/token/refresh/cookie/

# -b cookie.txt: Use the saved cookies
# -v: debug - optional.
```

## Admin Forbidden - CSRF cookie not set

<http://127.0.0.1:8000/admin/login/?next=/admin/>

This happened suddenly where django settings and CSRF settings were left unchanged. Reason for its cause is unknown.

Possible resolutions:
- (Working solution) at `settings.py` set: `SESSION_COOKIE_SECURE = True` `CSRF_COOKIE_SECURE = True`
- Access the admin page with `localhost` instead of `127.0.0.1`.
- Disable/white-list all extensions on the admin page (or as last resort, disable/remove browser's extensions).
- Remove browser cache and cookie on the admin page (or as last resort, remove browser's global cache and cookie).
- Try on another browser.
- Remove all .pyc python cache in the project and restart the server.

Note for the working solution: Read and be aware of the comments in the `settings.py`:
- for the development `HTTP` pages may not be accessible when making the admin pages accessible:

```py
# Enable these three only when using HTTPS
SECURE_SSL_REDIRECT = False
# Enable these two below only when accessing admin website
SESSION_COOKIE_SECURE = True 
CSRF_COOKIE_SECURE = True
```

Issue:
```html
Forbidden (403)

CSRF verification failed. Request aborted.

You are seeing this message because this site requires a CSRF cookie when submitting forms. This cookie is required for security reasons, to ensure that your browser is not being hijacked by third parties.

If you have configured your browser to disable cookies, please re-enable them, at least for this site, or for “same-origin” requests.
```

## Resolving CORS missing allow headers

`settings.py`

```py
CORS_ALLOW_HEADERS = [
    ...
    'content-type',
]
```

## Running ASGI server

`uvicorn ku_djangoo.asgi:application --host 0.0.0.0 --port 8000 --reload`

## Setting up ASGI

Core Libraries:

- ASGI Server Options:
  - Uvicorn: (Selected) A high-performance ASGI server based on uvloop and httptools.
  - Hypercorn: A flexible ASGI server that supports HTTP/1, HTTP/2, and WebSockets.   
  - Daphne: A production-ready ASGI server, often used with Django Channels.  

For Features and Scalability:

- Django Channels: This library extends Django to support real-time communication features like WebSockets. It is useful for updating user with progress of AI and dataset processes in the server. Channels is typically used for features like chat applications and real-time notifications.   
- Asyncio: Python's standard library for asynchronous programming, essential for writing efficient and scalable ASGI applications.

Considerations:

- Database Drivers: Ensure that the database driver supports asynchronous operations. Check `asyncpg`, an asynchronous PostgreSQL driver.
- Third-Party Libraries: Check the documentation to see if libraries have asynchronous support.
- Deployment: Choose a deployment platform that supports ASGI, such as Heroku, AWS, or Google Cloud Platform. Configure your deployment environment to use an ASGI server like Uvicorn or Hypercorn.

## Installing Minio

<https://github.com/minio/minio?tab=readme-ov-file>

Note: without `sudo` command permission restrictions may arrise. 

```sh
wget https://dl.min.io/server/minio/release/linux-amd64/minio
sudo chmod +x minio
sudo ./minio server /data
```

Terminal server response:  
Keep a note of the credentials.

```sh
API: http://10.144.127.231:9000  http://10.154.6.97:9000  http://100.75.219.92:9000  http://127.0.0.1:9000 
   RootUser: m********* 
   RootPass: m*********
```

Testing server-client connection;
- Server is on wired university network (likely an Eduroam network).
- Client device is on wireless Eduroam connection.

```sh
# Server:
ifconfig
enp2s0: ...
        inet 10.144.127.231 ... # Your IP will be different

# Client:
# Browser:
http://10.144.127.231:38963/login
# Minio login webpage appears: Enter the previously shown credentials. 
```
## Creating Access and Secret Key with Minio

<http://127.0.0.1:38963/access-keys/new-account>

Access key:  
a...

Secret key:  
b...

## Resolving address already in use

This may happen when exiting uvicorn server and restarting it.

```sh
uvicorn ku_djangoo.asgi:application --host 0.0.0.0 --port 8000 --reload
# ERROR:    [Errno 98] Address already in use

lsof -i :8000
# COMMAND      PID USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
# uvicorn   624372 user    3u  IPv4 4371939      0t0  TCP *:8000 (LISTEN)

kill <PID>      # Sends a SIGTERM signal (graceful termination)
kill -9 <PID>   # Sends a SIGKILL signal (forceful termination - use with caution)
```

## Testing APIs

MinIO read/write API tests:

```sh
curl \
  -X POST \
  -F "data=@static/dataset/CS_dataset/test/images/ppe_0000_jpg.rf.c102a9a7c8dec01565a8f95ff295974c.jpg" \
  http://localhost:8000/api/dataset/save-minio/test/

curl -X GET http://localhost:8000/api/dataset/minio/ -o tmp/downloaded_file.jpg

curl -X GET http://localhost:8000/api/dataset/minio/ -O -J

# Optionally, open the URL link in browser.
```

MinIO zip upload API test:

```sh
curl \
  -X POST \
  -F "data=@static/dataset/CS_dataset.zip" \
  http://localhost:8000/api/dataset/save-minio/test/

curl -X GET http://localhost:8000/api/dataset/get-minio/test/zip/ -o tmp/downloaded.zip
```

MinIO file delete API test:

```sh
curl \
  -X DELETE \
  http://localhost:8000/api/dataset/minio/
```

MinIO file update API test:

```sh
curl \
  -X PUT \
  -F "data=@static/dataset/CS_dataset.zip" \  
  http://localhost:8000/api/dataset/update-minio/test/
```

MinIO file list:

```sh
curl -X GET http://localhost:8000/api/dataset/minio/test/list/ -o tmp/downloaded.zip

~/minio --version
```

Testing Log in and log out APIs (cookie JWT tokens):

```sh
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -b cookie.txt -c cookie.txt \
  -d '{"username": "abc", "password": "***"}' \
  http://localhost:8000/api/token/login/cookie/

# response output:
# {"success": true, "username": "abc"}

curl \
  -X POST \
  -b cookie.txt -c cookie.txt \
  http://localhost:8000/api/token/check-login/cookie/

# response output:
# {"is_logged_in":true}

curl \
  -X POST \
  -b cookie.txt -c cookie.txt \
  http://localhost:8000/api/token/logout/cookie/

# response output:
# {"detail":"Successfully logged out.", "success": true}

# Call check-login API again: 
# response output:
# {"is_logged_in":false}
```

## Connecting to wireless Eduroam network on Linux

Security configuration:  
Security: WPA & WPA2 Enterprise  
Authentication: Protected EAP (PEAP)  
Anonymous identity: ku70001@kingston.ac.uk  
Password: ...  
Domain: kingston.ac.uk  
[x] No CA certificate is required  
PEAP version: Automatic  
Inner authentication: MSCHAPv2  
username: ku70001@kingston.ac.uk  
Password: ...  

## Creating a mount directory

This section will no longer be necessary and will be replaced by section Installing Minio.

Windows - file server
Ubuntu/Linux - API server

Either operating software may be used but setup will be different.

Windows > Settings > Network & Internet > Advanced network settings > Advanced sharing settings:
Option1. `All networks`: Have windows password setup and enable `Password-protected sharing`.
Option2. Do not have windows password setup and enable `Public folder sharing` (not recommended).
1. `Public networks`: enable `File and printer sharing`
2. `Private networks`: enable `Network discovery` and `File and printer sharing`
1. Alternative method: Windows Control Panel > System and Security > Windows Defender Firewall > Allowed applications > Enable Private and Public `File and Printer Sharing`

Use Tailscale (mesh) VPN on both devices (Ubuntu guide below)

1. Authenticate using the same account with same domain (Apple, Google, Microsoft, etc.)
2. or, Authenticate with different account and use "Invite external Users" by email. 
3. Tailwind will show IP addresses and a command to test `ping 100.78.7.23 -c 4`. Test ping from both devices.

Windows. Create a folder (e.g. `remote-storage`) in any directory to share and share to `Everyone` or `User` or groups that needs access. 

Ubuntu:
```sh
sudo apt-get install cifs-utils

curl -fsSL https://tailscale.com/install.sh | sh

sudo tailscale up

# Optional. Disconnect from Tailscale.
# sudo tailscale down

# Optionally test on different networks e.g. Eduroam and The Cloud.
ping 100.78.7.23 -c 4

sudo mkdir /mnt/remote-storage
# format
sudo mount -t cifs //<remote-computer-IP>/<remote-storage> /mnt/<local-mount-storage> -o username=<windows-username>,password=<my-password>,vers=3.0
# example
sudo mount -t cifs //100.78.7.23/remote-storage /mnt/remote-storage -o username=user,password=mypass,vers=3.0

# simple test
cd /mnt/remote-storage
sudo mkdir hello
```

## Optional - Making a beginner sample model data

Example of how to make an object and save to database.

```sh
# Writing your first Django app, part 2
# https://docs.djangoproject.com/en/5.1/intro/tutorial02/

# API - Interactive python shell
python3 manage.py shell

from polls.models import Choice, Question  # Import the model classes we just wrote.

Question.objects.all()
# <QuerySet []>  # No questions are in the system yet.

# Create a new Question.
from django.utils import timezone
q = Question(question_text="What's new?", pub_date=timezone.now())

# Save the object into the database. You have to call save() explicitly.
q.save()

q.id
# 1
q.question_text
# "What's new?"
q.pub_date
# datetime.datetime(2012, 2, 26, 13, 0, 0, 775217, tzinfo=datetime.timezone.utc)

# Change values by changing the attributes, then calling save().
q.question_text = "What's up?"
q.save()

Question.objects.all()
# <QuerySet [<Question: Question object (1)>]> 

# ctrl + z  to exit
```

## Choosing python version for debugging

VS Code  

`ctrl + shift + p`  
`>Python: Select Interpreter`  
Choose `Python 3.11.10 64-bit usr/bin/python`  
Or Choose the python version that have been used for the project development.

Download extension:  
Python Debugger  
v2024.12.0  
Microsoft  

`ctrl + shift + p`  
Choose `Debug: Select and Start Debugging`  
Choose `Python Debugger: DJango`  

Add breakpoints to where you want to view variable content, instead of using print() function.  

## Initialising a Github repository
git config

Install Git
```sh
sudo apt update
sudo apt upgrade
sudo apt install git
```

Initial user setup and make gitignore file 
```sh
touch .gitignore
# https://www.toptal.com/developers/gitignore
# Search: Django Python
# Copy content and paste to gitignore file 

git rm --cached FILENAME

git config --global user.email a@example.com
git config --global user.username ace

touch ~/.gitignore
code ~/.gitignore
# Copy-paste the gitignore content and save 
git config --global core.excludesFile ~/.gitignore
```

Initialise a Github Repository
```sh
git init
git add .
```

Commit the repository
```sh
# 1st option
git commit
# write commit message
ctrl+o
ctrl+x

# 2nd option
git commit -m 'your commit message'
```

## Installing Github Desktop on Linux

```sh
wget -qO - https://apt.packages.shiftkey.dev/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/shiftkey-packages.gpg > /dev/null
sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/shiftkey-packages.gpg] https://apt.packages.shiftkey.dev/ubuntu/ any main" > /etc/apt/sources.list.d/shiftkey-packages.list'

sudo apt update && sudo apt install github-desktop

github
```

## Excluding gitignore files 

```sh
git rm -rf --cached .
git add .

git commit
# follow above guide "Commit the repository"
# or use github desktop
```

## Deleting an environment

```sh
# myenv is in the current directory of the terminal 
rm -r myenv
```