from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.template.backends.base import BaseEngine
from django.template.engine import Engine
from django.template.context import make_context
from django.conf import settings
from django.contrib.auth import get_user
from django.middleware.csrf import rotate_token
import json
from django.utils.module_loading import import_string

class NuxtDjangoTemplateBackend(BaseEngine):
    # Name of the subdirectory containing the templates for this engine
    # inside an installed application.
    #app_dirname = "django_nuxt"

    def __init__(self, params):
        params = params.copy()
        options = params.pop("OPTIONS").copy()
        super().__init__(params)

        nuxt_generated_folder = getattr(settings, 'DJANGO_NUXT_GENERATED_FOLDER', 'ui/.output/public/')
        self.engine = Engine([nuxt_generated_folder], False, **options)

    def from_string(self, template_code):
        return Template(self.engine.from_string(template_code))

    def get_template(self, template_name):
        nuxt_template_name = getattr(settings, 'DJANGO_NUXT_TEMPLATE_NAME', '_nuxt')
        if template_name != nuxt_template_name:
            raise TemplateDoesNotExist(template_name)

        nuxt_server_running = getattr(settings, 'DJANGO_NUXT_SERVER_RUNNING', None)
        if settings.DEBUG or nuxt_server_running:
            import requests
            try:
                response = requests.get(nuxt_server_running or 'http://localhost:3000')
                if response.status_code == 200:
                    return Template(self.engine.from_string(response.text))
            except requests.RequestException:
              raise Exception(f"Nuxt is not running on {nuxt_server_running or 'localhost:3000'}")

        return Template(self.engine.get_template('200.html'))

class Template:
    def __init__(self, template):
        self.template = template

    def render(self, context=None, request=None):
        django_nuxt_data_processors = getattr(settings, 'DJANGO_NUXT_DATA_PROCESSORS', [])
        nuxt_django_prefix = getattr(settings, 'DJANGO_NUXT_PREFIX', 'NUXT_DJANGO_')

        context = make_context(
            context, request, autoescape=True
        )
        # Add all Django settings beginning with "NUXT_DJANGO_" to the context
        for s in dir(settings):
            if s.startswith(nuxt_django_prefix):
                context[s] = getattr(settings, s)

        if not context.get(f'{nuxt_django_prefix}BASE_URL'):
            context[f'{nuxt_django_prefix}BASE_URL'] = "/"

        user = get_user(request)

        if user.is_authenticated:
            perms = list(user.get_all_permissions())
            user_data = {
                "id": user.id,
                "username": user.username,
                "is_authenticated": True,
            }
        else:
            user_data = {
                "is_authenticated": False,
            }
            perms = []

        dj_data = {
            "user": user_data,
            "perms": perms,
        }
        scripts = []
        for processor in django_nuxt_data_processors:
            func = import_string(processor)
            data = func(context, request)
            if data:
                json_data = {}
                for key, value in data.items():
                    if key == "_scripts":
                        scripts.extend(value)
                    else:
                        json_data[key] = value

                dj_data.update(json_data)

        try:
            rendered = self.template.render(context)
        except TemplateDoesNotExist as exc:
            reraise(exc, self.backend)

        script_tag = f'<script>window.django_nuxt = {json.dumps(dj_data)}</script>'
        script_tag += "\n".join(scripts)
        rendered = rendered.replace('</head>', f'{script_tag}\n</head>')
        return rendered

def copy_exception(exc, backend=None):
    """
    Create a new TemplateDoesNotExist. Preserve its declared attributes and
    template debug data but discard __traceback__, __context__, and __cause__
    to make this object suitable for keeping around (in a cache, for example).
    """
    backend = backend or exc.backend
    new = exc.__class__(*exc.args, tried=exc.tried, backend=backend, chain=exc.chain)
    if hasattr(exc, "template_debug"):
        new.template_debug = exc.template_debug
    return new

def reraise(exc, backend):
    """
    Reraise TemplateDoesNotExist while maintaining template debug information.
    """
    new = copy_exception(exc, backend)
    raise new from exc