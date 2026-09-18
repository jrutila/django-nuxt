# django-nuxt
Django and Nuxt, match made in heaven

## Features

- Nuxt page is rendereder through Django
 - user and permissions are injected to the generated Nuxt page
- Nuxt static files are served from Django
- In development mode, Nuxt and Django live reloads are working
 - Django Debug Toolbar is working
 - Nuxt DevTools are working (Django reverse-proxies DevTools on port 8000; Vite modules and fonts redirect to Nuxt)

## Caveats

- Nuxt SSR is not supported, yet

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

`NuxtCatchAllUrls` reverse-proxies unmatched HTML to the Nuxt development server when it is running so Django can inject `window.django_nuxt`. DevTools (`/__nuxt_devtools__/`) stay on the Django origin (usually port 8000). Vite modules (`/_nuxt/`) and fonts (`/fonts/`, `/_fonts/`) 302-redirect to Nuxt (usually port 3000) so HMR and assets skip Django's connection budget. If the Nuxt server is not running, Django loads the generated `200.html` template.

For development (`settings.DEBUG = True`), run the Nuxt development server at the same time as Django. Open the app at `http://localhost:8000/` — do not use port 3000 as the page origin.

The Nuxt module defaults the Django page origin to `http://localhost:8000` (used for `allowedHosts` and CORS). Override it with `nuxtDjango.devOrigin` or the `NUXT_DJANGO_DEV_ORIGIN` environment variable.

For production, generate the Nuxt files with `nuxt generate` and then collect the static files with `python manage.py collectstatic`.

Remember, when serving the Nuxt static files (`_nuxt` folder) in production, you might have to configure that independent from other Django static files as Nuxt tries to find the files under the `/_nuxt/` path, not `/static/_nuxt/`.

## Settings

### DJANGO_NUXT_SERVER_RUNNING

The URL of the Nuxt development server that Django reverse-proxies to. Default is `http://localhost:3000`.
This value should be `None` or `False` in production.

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

### Nuxt `devOrigin` / `NUXT_DJANGO_DEV_ORIGIN`

Public origin the browser uses in development (the Django server). Default is `http://localhost:8000`. Set this on the Nuxt module when Django is not on port 8000:

```ts
export default defineNuxtConfig({
  modules: ['@jrutila/nuxt-django'],
  nuxtDjango: {
    devOrigin: 'http://localhost:8000',
  },
})
```

Or export `NUXT_DJANGO_DEV_ORIGIN=http://localhost:8000` when starting Nuxt.
