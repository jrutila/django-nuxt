from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

def NuxtStaticUrls():
    if settings.DEBUG:
        from django.views.generic import View
        from django.http import HttpResponse
        
        class NuxtProxyView(View):
            def get(self, request, *args, **kwargs):
                from django.shortcuts import redirect
                try:
                    return redirect('http://localhost:3000' + request.path)
                except:
                    return HttpResponse("Nuxt is not running on localhost:3000", status=503)
        
        return [
            path('_nuxt/<path:path>', NuxtProxyView.as_view(), name='nuxt_proxy'),
            path('__nuxt_devtools__/<path:path>', NuxtProxyView.as_view(), name='nuxt_devtools_proxy')
        ]

    return [
        re_path(r'^_nuxt/(?P<path>.*)$', serve, kwargs={
            'document_root': f'{settings.STATIC_ROOT}/_nuxt',
        }),
    ]

def NuxtCatchAllUrls():
    from django_nuxt import views

    return [
        re_path(r'^(?!\.).*$', views.nuxt_proxy, name='nuxt_catch_all'),
    ]