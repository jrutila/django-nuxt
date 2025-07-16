# django-nuxt
Django and Nuxt, match made in heaven

## Features

- Nuxt page is rendereder through Django
 - user and permissions are injected to the generated Nuxt page
- Nuxt static files are served from Django
- In development mode, Nuxt and Django live reloads are working
 - Django Debug Toolbar is working
 - Nuxt devtools are not working, yet

## Caveats

- Nuxt SSR is not supported, yet
- Nuxt devtools are not working, yet

## Installation

```bash
pip install django-nuxt
```

## Usage

In the `settings.py` file, add the following:

```python
TEMPLATES = [
    ...,
    {
        'BACKEND': 'django_nuxt.backends.NuxtDjangoTemplateBackend',
    },
]
STATICFILES_FINDERS = [
    ...
    'django_nuxt.staticfiles.NuxtStaticFilesFinder',
]
```

and in the project's `urls.py` file, add the following:	

```python
from django_nuxt.urls import NuxtStaticUrls, NuxtCatchAllUrls

urlpatterns = [
    ...,
] + NuxtStaticUrls() + NuxtCatchAllUrls()
```

For development (settings.DEBUG = True), have the Nuxt development server running the same time with
Django development server.

For production, generate the Nuxt files with `nuxt generate` and then collect the static files with `python manage.py collectstatic`.

## Settings

### DJANGO_NUXT_SERVER_RUNNING

The URL of the Nuxt development server. Default is `http://localhost:3000`.
This value should be None in production.

### DJANGO_NUXT_GENERATED_FOLDER

The folder where the Nuxt generated files are stored. Default is `ui/.output/public/`.

### DJANGO_NUXT_PUBLIC_FOLDER

The folder where the Nuxt public files are stored. Will be collected to static files. Default is `ui/public/`.

### DJANGO_NUXT_DATA_PROCESSORS

A list of functions that will be called to process the data for the Nuxt page. Injected into `window.django_nuxt` object. Default is an empty list.

### DJANGO_NUXT_PREFIX

The prefix for the Django settings that will be injected to the Nuxt page. Default is `NUXT_DJANGO_`.

By default, injects the following settings:
- NUXT_DJANGO_BASE_URL

### DJANGO_NUXT_TEMPLATE_NAME

The name of the template that will be used to render the Nuxt page. This should not be changed. Default is `_nuxt`.
