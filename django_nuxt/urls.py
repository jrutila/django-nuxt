from django.conf import settings
from django.urls import re_path
from django.views.static import serve

from django_nuxt.conf import get_nuxt_dev_server_url


def _dev_proxy_urls(name):
    from django_nuxt.proxy import NuxtDevProxyView

    return [
        re_path(r"^(?!\.).*$", NuxtDevProxyView.as_view(), name=name),
    ]


def NuxtStaticUrls():
    """
    Serve Nuxt files through Django.

    In development, reverse-proxies all unmatched requests to the Nuxt server.
    This should not be used in production!
    """
    if get_nuxt_dev_server_url():
        return _dev_proxy_urls("nuxt_proxy")

    dj_static_root = getattr(settings, "DJANGO_NUXT_STATIC_ROOT", None)
    nuxt_assets_dir = getattr(settings, "DJANGO_NUXT_GENERATED_ASSETS_DIR", "_nuxt/")
    if dj_static_root is None and settings.DEBUG:
        nuxt_generated_folder = getattr(settings, "DJANGO_NUXT_GENERATED_FOLDER", "ui/.output/public/")
        document_root = f"{nuxt_generated_folder}{nuxt_assets_dir}"
    else:
        document_root = f"{dj_static_root or settings.STATIC_ROOT}/{nuxt_assets_dir}"

    dj_static_url = getattr(settings, "DJANGO_NUXT_STATIC_URL", "")
    nuxt_static_url = f"{dj_static_url}{nuxt_assets_dir}"

    return [
        re_path(fr"^{nuxt_static_url}(?P<path>.*)$", serve, kwargs={
            "document_root": document_root,
        }),
    ]


def NuxtCatchAllUrls():
    from django_nuxt import views

    if get_nuxt_dev_server_url():
        return _dev_proxy_urls("nuxt_catch_all")

    nuxt_static_urls = []
    if settings.DEBUG:
        nuxt_static_urls = NuxtStaticUrls()

    return nuxt_static_urls + [
        re_path(r"^(?!\.).*$", views.nuxt_proxy, name="nuxt_catch_all"),
    ]
