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
from django_nuxt.urls import NuxtCatchAllUrls

urlpatterns = [
    ...,
] + NuxtCatchAllUrls()
```

`NuxtCatchAllUrls` is a proxy that will forward all requests to the Nuxt development server if the server is running or load the default `200.html` template. When in DEBUG mode, it will also serve the Nuxt static files with a proxy view.

For development (settings.DEBUG = True), have the Nuxt development server running the same time with Django development server.

For production, generate the Nuxt files with `nuxt generate` and then collect the static files with `python manage.py collectstatic`.

Remember, when serving the Nuxt static files (`_nuxt` folder) in production, you might have to configure that independent from other Django static files as Nuxt tries to find the files under the `/_nuxt/` path, not `/static/_nuxt/`.

## Settings

### DJANGO_NUXT_SERVER_RUNNING

The URL of the Nuxt development server. Default is `http://localhost:3000`.
This value should be None in production.

### DJANGO_NUXT_GENERATED_FOLDER

The folder where the Nuxt generated files are stored. Default is `ui/.output/public/`.

### DJANGO_NUXT_GENERATED_ASSETS_DIR

The folder inside the DJANGO_NUXT_GENERATED_FOLDER folder that will be used to serve the Nuxt static files (not the 200.html, but the _nuxt folder). Default is `_nuxt/`.

This affects the Django static file collecting. Remember, when you serve the files, by default, Nuxt tries to find the files under the `/_nuxt/` path, not `/static/`.

#### Serving the nuxt files with WhiteNoise

If you are using WhiteNoise, you can set the `DJANGO_NUXT_GENERATED_ASSETS_DIR` to `static/_nuxt/` so that WhiteNoise can serve the Nuxt static files. When generating the Nuxt build, run it with `NUXT_APP_BUILD_ASSETS_DIR=/static/_nuxt/ nuxt generate` so that Nuxt tries to find the `_nuxt` files under the `static` path.

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

### DJANGO_NUXT_STATIC_URL

If you really need to fine tune the NuxtStaticUrls helper, you can set the `DJANGO_NUXT_STATIC_URL` to the prefix that will be used to serve the Nuxt static files. Default is an empty string.

Remember, you should not use NuxtStaticUrls in production!
