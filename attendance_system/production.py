from attendance_system.settings import *

DEBUG = True

SECRET_KEY = 'django-insecure-jri&oovjjn_5)uq#!6tbr=@z((!_!0s$(^ch@8+p$2k+cuh2b8'

ALLOWED_HOSTS = ['127.0.0.1:5500', 'sensorhub.pythonanywhere.com']

STATIC_ROOT = '/home/sensorhub/sensor_hub/static'

MEDIA_URL = '/media/'

MEDIA_ROOT = '/home/sensorhub/sensor_hub/static/media'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sensorhub$default',
        'USER': 'sensorhub',
        'PASSWORD': "Wubbalubbadubdub291998",
        'HOST': 'sensorhub.mysql.pythonanywhere-services.com',
    }
}


print("IM NOT HERE")