# django-nuxt
Django and Nuxt, match made in heaven

# Tutorial

Making the project that is present in the `example/simple` folder.

# Setup

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

# Add a new app

```bash
python manage.py startapp simple_app
```
