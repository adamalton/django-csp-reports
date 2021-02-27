"""Settings for cspreports tests."""
SECRET_KEY = 'CSP_REPORTS_TESTS'

INSTALLED_APPS = [
    'cspreports',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]
