from attendance_system.settings import *

DEBUG = False

SECRET_KEY = 'django-insecure-jri&oovjjn_5)uq#!6tbr=@z((!_!0s$(^ch@8+p$2k+cuh2b8'

ALLOWED_HOSTS = ['127.0.0.1:5500', 'attendancehub.pythonanywhere.com']

STATIC_ROOT = '/home/attendancehub/Attendance-System/static'

MEDIA_URL = '/media/'

MEDIA_ROOT = '/home/attendancehub/Attendance-System/static/media'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'attendancehub$default',
        'USER': 'attendancehub',
        'PASSWORD': "K1yUDI!'TwC:`)gwCsz-hm&^`",
        'HOST': 'attendancehub.mysql.pythonanywhere-services.com',
    }
}


print("IM NOT HERE")