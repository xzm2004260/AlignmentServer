Lyric-Find Dataset
--------------
Cross-check audio from LF and annoation present from Mauch and Gracenote
Case 1) separation with DeepConvSep
Case 2) separation with Audionamix

1. check that lyrics .lrc are the same as .wordonsets (and respectively .txt) or at least that they have same num tokens
Load in beyond compare .txt and .lrc.

2. Make sure that the annotation .wordonsets corresponds to the audio from LF
- open in audacity
- python ~/workspace/lakh_vocal_segments_dataset/scripts/shift_time_annotaion.py ~/Documents/VOICE_magix/Lyric_find/19-lyrics/ABBA\ -\ Knowing\ Me\,\ Knowing\ You.wordonset.tsv <time1>
Assume that the line-level annotation has no errors.

3. Time shift audio of the _vocal.wav_ version with same <time1>



4. Align
source ~/.virtualenvs/alana/bin/activate
python3 ~/workspace/AlignmentServer/scripts/run_all_lyric_find.py 0 for case 1 and 
python3 ~/workspace/AlignmentServer/scripts/run_all_lyric_find.py 1 for case 2

5. Eval
case 1)
python /Users/joro/workspace/AlignmentEvaluation/align_eval/eval.py       "/Users/joro/Documents/VOICE_magix/Lyric_find/19-lyrics/" "/Users/joro/Documents/VOICE_magix/Lyric_find/19-lyrics/" . 0.5

case 2)
python /Users/joro/workspace/AlignmentEvaluation/align_eval/eval.py       "/Users/joro/Documents/VOICE_magix/Lyric_find/19-lyrics/" "/Users/joro/Documents/VOICE_magix/Lyric_find/19-lyrics/audionamix_separated/" . 0.5


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

- Set the env var DJANGO_SETTINGS_MODULE
DJANGO_SETTINGS_MODULE=Magixbackend.setting.test
or 
DJANGO_SETTINGS_MODULE=Magixbackend.setting.production. 
Default is test, being set in manage.py

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
- Setting up the postgres Database
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

Steps to production
----------------
- Uncomment authentication classes in model/alignment
- 
- Create super User

```sh
$ python manage.py createsuperuser --username=mirza123 --email=mirza@gmail.com // unique username
```
- To add users login with superuser http://localhost:8000/admin/
- Enter basic information about user including random password to create user.
  Uncheck the is_active of user so that when user change password then user will be active.
- Give unique username to the concerned clients so that they can change password with given username at 
  endpoint http://localhost:8000/auth/password/change
- After changing old password to new one, users can sign in at endpoint http://localhost:8000/auth/signin
- Token will be expire after 7 days from sign in by user.

Documentation
-------------
- https://documenter.getpostman.com/view/2377788/magixbackend/RVu1JBf9
