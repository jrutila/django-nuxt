from django.shortcuts import render
from django.conf import settings

nuxt_template_name = getattr(settings, 'DJANGO_NUXT_TEMPLATE_NAME', '_nuxt')

def nuxt_proxy(request):
    return render(request, nuxt_template_name)
