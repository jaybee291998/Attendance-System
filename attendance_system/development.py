from attendance_system.settings import *


STATICFILES_DIRS = [
    BASE_DIR / "static",
]

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

STATIC_ROOT = os.path.join(BASE_DIR, '/static')

print("IM HERE")