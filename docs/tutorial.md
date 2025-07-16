# Tutorial

Making the project that is present in the `example/simple` folder.

## Setup

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the dependencies
# Copy the requirements.txt file to the project root
pip install -r requirements.txt

# Activate the virtual environment
source venv/bin/activate

mkdir simple
django-admin startproject simple simple
```

You should have a project structure like this:

```
- manage.py
- simple/settings.py
- simple/urls.py
- simple/wsgi.py
- simple/asgi.py
- simple/static
- simple/templates


You can now run the project with `python manage.py runserver`. You should see the default Django welcome page.

## Add a new app

```bash
python manage.py startapp simple_app
```

Add the app to the `INSTALLED_APPS` in the `simple/settings.py` file.

```python
INSTALLED_APPS = [
    ...
    'simple_app',
    ...
]
```

Add the model to the `models.py` file.

```python
from django.db import models

class Todo(models.Model):
  title = models.CharField(max_length=200)
```

Run the migrations.

```bash
python manage.py makemigrations
python manage.py migrate
```

# See the app in the admin panel

```bash	
python manage.py createsuperuser
```

# Add the app to the admin panel

```python
from django.contrib import admin
from .models import Todo

admin.site.register(Todo)
```

You should now to login to the admin panel with the credentials you created and see the Todo model in the admin panel.

So far, we have done pretty much basic Django setup.

## Setup Nuxt

```bash
npm create nuxt ui
```

You should have a project structure like this:

```
- manage.py
- simple/settings.py
- ui/app/app.vue
- ui/nuxt.config.ts
```

Try it out with `npm run dev`. You should see the Nuxt welcome page.


## Let's integrate the basics

### urls.py

In the `simple/urls.py` file, add the following:
	
```python
from django.contrib import admin
from django.urls import path, include
from django_nuxt.urls import NuxtStaticUrls

urlpatterns = [
    path('admin/', admin.site.urls),
] + NuxtStaticUrls()
```

This will take care of the Nuxt static files (beginning with `_nuxt/`) in django DEBUG mode _and_ in production.

You can test that the proxy works. Load the Nuxt welcome page in the browser (usually `http://localhost:3000`) and look for any `_nuxt/` requests.

For example, I had this in the network tab: `http://localhost:3000/_nuxt/@fs/path/django-nuxt/example/simple/ui/node_modules/nuxt/dist/app/components/welcome.vue?vue&type=style&index=0&scoped=8ffa6876&lang.css`

Now, copy the URL and change the port to Django port (usually `8000`). You should see the same file loaded correctly. (It does a redirect.)

### Nuxt proxy view

`django-nuxt` provides a view that can be used to proxy Nuxt requests to Django.

In the `simple/urls.py` file, add the following:

```python
from django.contrib import admin
from django.urls import path
from django_nuxt.urls import NuxtStaticUrls, NuxtCatchAllUrls

urlpatterns = [
    path('admin/', admin.site.urls),
] + NuxtStaticUrls() + NuxtCatchAllUrls()
```

If you now try to open the Django page `http://localhost:8000/` you should see `TemplateDoesNotExist at /_nuxt` error. This means the `NuxtCatchAllUrls` is working.

What we still need to add is the template backend for the Nuxt pages.

In the `simple/settings.py` file, add the following:

```python
TEMPLATES = [
    {
        'BACKEND': 'django_nuxt.backends.NuxtDjangoTemplateBackend',
    },
]
```

If you now navigate to the _Django_ page `http://localhost:8000/` you should see the _Nuxt_ welcome page. Magic!