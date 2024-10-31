# django-model-api-server

## Developer Commands 

```sh
sudo apt update
python3 -V
sudo apt install python3-django
django-admin --version
# 4.2.11

python3.11 -m pip list | grep ja
# Django 4.2.11

sudo apt update
python3 -V
sudo apt install python3-pip python3-venv
sudo apt install python3-dev

# check pip version
python3.11 -m pip --version

mkdir ~/newproject
cd ~/newproject

# make env
python3 -m venv my_env
# Python 3.12
# Throughout the whole document, it was tried best to use python 3.11 for stability but using it is causing troubles, stick with 3.12 if preferred. 
# in practise use `python` or `python3.12 -m` instaed of `python3.11 -m`

# check current env
python
import sys
print(sys.prefix)
# /home/user/my_env
# ctrl + z to exit
# /usr

python3.11 -V
# Python 3.11.10

cd /home/user/Documents/ku_django/
source /home/user/my_env/bin/activate

# python3.11 -m pip install django
pip install django

# A Guide from Writing your first Django app
# https://docs.djangoproject.com/en/5.1/intro/tutorial01/

# python3.11 -m django --version
# 4.2.11

python -m django --version
# 5.1.2

django-admin --version
# 5.1.2

deactivate

# create a project
# note make sure to always replace python, python3 and python3.12 to python3.11.
django-admin startproject ku_django
cd ku_django/

# python3.11 manage.py runserver
python manage.py runserver

# create an app
# make sure to replace "polls" to webapp
# python3.11 manage.py startapp webapp
python manage.py startapp webapp

# start django
cd /home/user/Documents/ku_django/
source /home/user/my_env/bin/activate
deactivate

django-admin startproject djangoproject .

# migrate database
python manage.py migrate

python manage.py createsuperuser

# verify that wired an index view into the URLconf 
python manage.py runserver

# Writing your first Django app, part 2
# https://docs.djangoproject.com/en/5.1/intro/tutorial02/
python manage.py migrate

python3.11 manage.py makemigrations polls

python3.11 manage.py sqlmigrate polls 0001

# run migrate again to create those model tables in your database:
python3.11 manage.py migrate

# API - Interactive python shell
python3.11 manage.py shell

from polls.models import Choice, Question  # Import the model classes we just wrote.

# No questions are in the system yet.
Question.objects.all()
# <QuerySet []>

# Create a new Question.
# Support for time zones is enabled in the default settings file, so
# Django expects a datetime with tzinfo for pub_date. Use timezone.now()
# instead of datetime.datetime.now() and it will do the right thing.
from django.utils import timezone
q = Question(question_text="What's new?", pub_date=timezone.now())

# Save the object into the database. You have to call save() explicitly.
q.save()

# Now it has an ID.
q.id
# 1

# Access model field values via Python attributes.
q.question_text
# "What's new?"
q.pub_date
# datetime.datetime(2012, 2, 26, 13, 0, 0, 775217, tzinfo=datetime.timezone.utc)

# Change values by changing the attributes, then calling save().
q.question_text = "What's up?"
q.save()

# objects.all() displays all the questions in the database.
Question.objects.all()
# <QuerySet [<Question: Question object (1)>]>

# ctrl + z  to exit

# delete a environment
# myenv is in the same directory as terminal current directory 
rm -r myenv

```

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

python manage.py makemigrations
python manage.py migrate

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

# Migrations for 'polls':
#   polls/migrations/0001_initial.py
#     + Create model Question
#     + Create model Choice

python manage.py sqlmigrate polls 0004
python manage.py sqlmigrate polls 0005
python manage.py sqlmigrate polls 0006

# BEGIN;
# --
# -- Create model Question
# --
# CREATE TABLE "polls_question" (
#     "id" bigint NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
#     "question_text" varchar(200) NOT NULL,
#     "pub_date" timestamp with time zone NOT NULL
# );
# ...
# COMMIT;

python manage.py migrate

python manage.py shell
```

## Creating an admin or superuser

```sh
python manage.py createsuperuser

# Username: admin
# Email address: admin@example.com

# Password: ku202425
# Password (again): ku202425
# Superuser created successfully.

python manage.py runserver
```

## Creating first login database record

```sh
python manage.py shell

from polls.models import Login

Login.objects.all()

l = Login(email="ace@email.com", password="ace133", username="ace")

l.save()

l.id
l.email
l.password
l.username

Login.objects.all()

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

## Saving Python Packages and versions

```sh
pip freeze > requirements.txt
```

## Hiding Sidebar at mobile screen

Bootstrap
Layout Breakpoints
```
Breakpoint 	        Class infix 	Dimensions
Extra small 	    None 	        <576px
Small   	        sm 	            ≥576px
Medium 	            md 	            ≥768px
Large 	            lg 	            ≥992px
Extra large 	    xl 	            ≥1200px
Extra extra large 	xxl 	        ≥1400px
```

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

## Uploading folder to a directory

```py

# polls/models.py

# option 1
# https://stackoverflow.com/questions/65588269/how-can-i-create-an-upload-to-folder-that-is-named-a-field-belonging-to-the-mode

class Upload(models.Model):
    def user_directory_path(instance, filename):        
        return 'user_{0}/{1}'.format(instance.user.id, filename) # uploaded to MEDIA_ROOT/user_<id>/<filename>

# option 2
# https://forum.djangoproject.com/t/how-to-zip-files/17197/1

class Upload(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def save_folder(instance, filename):
        upload_to = ''
        ext = filename.split('.')[-1]
        filename = '{}_{}.{}'.format('classA', instance.uuid, ext)
        return os.path.join(upload_to, filename)
    folder = models.FileField(upload_to=save_folder, null = True , blank = True )
    

# option 3.1
# upload image instead of folder
# https://bdvade.hashnode.dev/structuring-file-uploads-in-django

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

# option 3.2
class Article(models.Model):
    ...
    image = models.ImageField(upload_to='%Y/%m/%d')
    # 
    # 2018/06/12/cover.jpg

# option 3.3
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
2. Second possible issue is that the location of the JavaScript was placed outside of a 'div' document container, whereas it should be placed right under the form document - under where the "</form>" ends. 

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