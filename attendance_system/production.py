from attendance_system.settings import *

DEBUG = False

SECRET_KEY = os.getenv("SECRET_KEY")
PROD_HOSTS = os.getenv("PROD_HOSTS")

ALLOWED_HOSTS = ['127.0.0.1:5500']
ALLOWED_HOSTS.append(PROD_HOSTS)

STATIC_ROOT = '/home/attendancehub/Attendance-System/static'

MEDIA_URL = '/media/'

MEDIA_ROOT = '/home/attendancehub/Attendance-System/static/media'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'attendancehub$default',
        'USER': 'attendancehub',
        'PASSWORD': os.getenv("PROD_DB_PASS"),
        'HOST': os.getenv("PROD_DB_HOST"),
    }
}


print("IM NOT HERE")