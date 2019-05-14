from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%r_4xljyo=g-3em2(ma8g+(5a9yz!c))^wkysqm%x4eu0$7935'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*', ]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *
except ImportError:
    pass
