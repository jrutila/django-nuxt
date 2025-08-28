from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

def NuxtStaticUrls():
    nuxt_server_running = getattr(settings, 'DJANGO_NUXT_SERVER_RUNNING', None)
    if nuxt_server_running != False or (settings.DEBUG and nuxt_server_running is None):
        if nuxt_server_running is True or nuxt_server_running is None:
            nuxt_server_running = 'http://localhost:3000'
        from django.views.generic import View
        from django.http import HttpResponse
        
        class NuxtProxyView(View):
            def get(self, request, *args, **kwargs):
                from django.shortcuts import redirect
                try:
                    return redirect(nuxt_server_running + request.path)
                except:
                    return HttpResponse(f"Nuxt is not running on {nuxt_server_running}", status=503)
        
        return [
            path('_nuxt/<path:path>', NuxtProxyView.as_view(), name='nuxt_proxy'),
            path('__nuxt_devtools__/<path:path>', NuxtProxyView.as_view(), name='nuxt_devtools_proxy')
        ]

    dj_static_root = getattr(settings, "DJANGO_NUXT_STATIC_ROOT", None)
    if dj_static_root is None and settings.DEBUG:
        nuxt_generated_folder = getattr(settings, 'DJANGO_NUXT_GENERATED_FOLDER', 'ui/.output/public/')
    else:
        nuxt_generated_folder = getattr(settings, "DJANGO_NUXT_STATIC_ROOT", settings.STATIC_ROOT)

    return [
        re_path(r'^_nuxt/(?P<path>.*)$', serve, kwargs={
            'document_root': f'{nuxt_generated_folder}/_nuxt',
        }),
    ]

def NuxtCatchAllUrls():
    from django_nuxt import views

    return [
        re_path(r'^(?!\.).*$', views.nuxt_proxy, name='nuxt_catch_all'),
    ]