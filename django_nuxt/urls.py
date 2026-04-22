from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

def NuxtStaticUrls():
    """
    Serve the Nuxt static files with a proxy view.
    This should not be used in production!
    """
    nuxt_server_running = getattr(settings, 'DJANGO_NUXT_SERVER_RUNNING', None)
    # Only use the proxy if explicitly set or not explicitly set in DEBUG mode
    if nuxt_server_running or (settings.DEBUG and nuxt_server_running is None):
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
    nuxt_assets_dir = getattr(settings, 'DJANGO_NUXT_GENERATED_ASSETS_DIR', '_nuxt/')
    if dj_static_root is None and settings.DEBUG:
        nuxt_generated_folder = getattr(settings, 'DJANGO_NUXT_GENERATED_FOLDER', 'ui/.output/public/')
        document_root = f'{nuxt_generated_folder}{nuxt_assets_dir}'
    else:
        document_root = f'{dj_static_root or settings.STATIC_ROOT}/{nuxt_assets_dir}'
    
    dj_static_url = getattr(settings, 'DJANGO_NUXT_STATIC_URL', "")
    nuxt_static_url = f'{dj_static_url}{nuxt_assets_dir}'

    return [
        re_path(fr'^{nuxt_static_url}(?P<path>.*)$', serve, kwargs={
            'document_root': document_root,
        }),
    ]

def NuxtCatchAllUrls():
    from django_nuxt import views

    nuxt_static_urls = []
    if settings.DEBUG:
        nuxt_static_urls = NuxtStaticUrls()

    return nuxt_static_urls + [
        re_path(r'^(?!\.).*$', views.nuxt_proxy, name='nuxt_catch_all'),
    ]