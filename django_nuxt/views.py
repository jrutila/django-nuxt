from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie

nuxt_template_name = getattr(settings, 'DJANGO_NUXT_TEMPLATE_NAME', '_nuxt')

@ensure_csrf_cookie
def nuxt_proxy(request):
    return render(request, nuxt_template_name)
