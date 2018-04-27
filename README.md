Magix Backend
----------------
Magix is a Music Technology product. A software based on Artificial Intelligence that
accepts as inputs the voice and the text and extracts the time information for each word.
Focused on voice recordings with a musical background
- singing and speech with music in the background.
This platform contains restfull APIs for the client end applications.

Requirements
------------

- Python 3.6.3
- Django 2.0.3
- Django Rest Framework 3.7.7
- Postgres

Installation
------------
Following are the steps to install this platform.

- Create Virtual Environment
```sh
$ virtualenv magixbackend-venv --python=python3
$ cd magixbackend-venv
$ source bin/activate
```
- Install Requirements
```sh
$ pip install -r requirements.txt
```
- Setting up the Database
```sh
$ cd Magixbackend
$ pwd //It should display like this "/Users/(user)/Magixbackend/Magixbackend"
$ sudo vim local_settings.py
    //Add the code below and save the file
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'magix_backend',
            'USER': 'username',
            'PASSWORD': 'password',
            'HOST': 'localhost',
            'PORT': '',
        }
    }
    // Note: Settings are for POSTGRES SQL
$ cd ..
$ python manage.py migrate
```
- Create Superuser
```sh
$ python manage.py createsuperuser --username=mirza123 --email=mirza@gmail.com // unique username
$ To add users login with superuser 127.0.0.1:8000/admin/
$ Enter basic information about user including random password to create user.
$ Assign unique username to the concerned clients so that they can change password with given username.
$ After changing password, users can sign in.
$ Expiry date of token will be 7 days from changing the password by user.
```