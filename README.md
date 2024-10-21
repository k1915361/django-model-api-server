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
# Throughout the whole document, it was tried best to use python 3.11 for stability but using it is causing trouble, stick with 3.12 if preferred. 
# troubles such as `python3.11 -m manage.py migrate` freezing and not running normally.
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

python3.11 manage.py makemigrations webapp

python3.11 manage.py sqlmigrate webapp 0001

# run migrate again to create those model tables in your database:
python3.11 manage.py migrate

# API - Interactive python shell
python3.11 manage.py shell

from webapp.models import Choice, Question  # Import the model classes we just wrote.

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

export DJANGO_SETTINGS_MODULE=webapp.settings
```

## Making migrations to database

https://docs.djangoproject.com/en/5.1/intro/tutorial02/

```sh
python manage.py makemigrations polls

# Migrations for 'polls':
#   polls/migrations/0001_initial.py
#     + Create model Question
#     + Create model Choice

python manage.py sqlmigrate polls 0001

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

# Creating
python manage.py createsuperuser

# Username: admin
# Email address: admin@example.com

# Password: ku202425
# Password (again): ku202425
# Superuser created successfully.

python manage.py runserver
```
