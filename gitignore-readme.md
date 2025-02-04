## Introduction

This is a file where credentials and sensitive data is stored.

## Creating an admin or superuser

DJango admin username and password:  
`admin`  
`ku202425`  

Other username and password:  
`ace`  
`ace13324`

`bob`  
`bob60624`

## Updating user database record

```sh
python manage.py shell

from polls.models import User

User.objects.all()

u = User.objects.filter(username="ace")[0]
u.id
u.email
u.username
u.password
u.set_password("ace13324")
u.password
u.save()

# ctrl + z  to exit python shell
```

## API tests

```sh
cd ~/Documents/ku_django

curl \
  -X POST \
  -H "Content-Type: application/json" \
  -b cookie.txt -c cookie.txt \
  -d '{"username": "admin", "password": "ku202425"}' \
  http://localhost:8000/api/token/login/cookie/

curl \
  -X POST \
  -H "Content-Type: application/json" \
  -v -b cookie.txt -c cookie.txt \
  -d '{}' \
  http://localhost:8000/api/token/refresh/cookie/

curl \
  -X GET http://localhost:8000/api/dataset/download/174 \
  -v -b cookie.txt -c cookie.txt \
  -o dataset.zip

curl \
  -X GET http://localhost:8000/api/dataset/download/test/ \
  -o dataset.zip

curl \
  -X POST \
  -F "data=@static/dataset/CS_dataset/test/images/ppe_0000_jpg.rf.c102a9a7c8dec01565a8f95ff295974c.jpg" \
  http://localhost:8000/api/dataset/save-minio/test/

curl -X GET http://localhost:8000/api/dataset/get-minio/test/ -o tmp/downloaded_file.jpg

curl -X GET http://localhost:8000/api/dataset/get-minio/test/ -O -J tmp/
```

Testing Log in and log out APIs (cookie JWT tokens):

```sh
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -b cookie.txt -c cookie.txt \
  -d '{"username": "admin", "password": "ku202425"}' \
  http://localhost:8000/api/token/login/cookie/

# response output:
# {"success": true, "username": "admin"}

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
# {"detail":"Successfully logged out.", "success": true }

# Call check-login API again: 
# response output:
# {"is_logged_in":false}
```

Go to `README.md`'s section `Testing APIs` for more tests.

## Creating a mount directory

`sudo mount -t cifs //100.78.7.23/remote-storage /mnt/remote-storage -o username=user,password=#,vers=3.0`

## Creating Access and Secret Key with Minio

<http://127.0.0.1:38963/access-keys/new-account>

Access key:  
wSEcMRT9rj2Jzcj7BBOp

Secret key:
ypCUmae6Sx1fbQIcLubx5G4TqlyPQixKperd3juG

# Remote Minio Server 

```
uprem0003-044355.kingston.ac.uk:9001
 
ROOTNAME
CHANGEME123
 
```