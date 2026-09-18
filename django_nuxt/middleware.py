from django.conf import settings
from django.shortcuts import redirect

from django_nuxt.conf import get_nuxt_dev_server_url

ASSET_MIDDLEWARE = "django_nuxt.middleware.NuxtAssetProxyMiddleware"

# Vite modules and fonts: 302 to Nuxt so the browser talks to :3000 directly.
NUXT_REDIRECT_PREFIXES = (
    "/_nuxt/",
    "/_fonts/",
    "/fonts/",
)
NUXT_REDIRECT_EXACT = (
    "/_nuxt",
    "/_fonts",
    "/fonts",
)

# DevTools must stay same-origin with the Django page.
NUXT_PROXY_PREFIXES = (
    "/__nuxt_devtools__/",
)
NUXT_PROXY_EXACT = (
    "/__nuxt_devtools__",
)


def _matches(path, exact, prefixes):
    return path in exact or path.startswith(prefixes)


def is_nuxt_redirect_path(path):
    return _matches(path, NUXT_REDIRECT_EXACT, NUXT_REDIRECT_PREFIXES)


def is_nuxt_proxy_path(path):
    return _matches(path, NUXT_PROXY_EXACT, NUXT_PROXY_PREFIXES)


def is_nuxt_asset_path(path):
    return is_nuxt_redirect_path(path) or is_nuxt_proxy_path(path)


def install_asset_proxy_middleware():
    """Put the asset proxy first so session/auth never run for Vite files."""
    middleware = list(settings.MIDDLEWARE)
    if ASSET_MIDDLEWARE not in middleware:
        settings.MIDDLEWARE = [ASSET_MIDDLEWARE, *middleware]


class NuxtAssetProxyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        upstream = get_nuxt_dev_server_url()
        if not upstream:
            return self.get_response(request)

        if is_nuxt_redirect_path(request.path):
            return redirect(upstream.rstrip("/") + request.get_full_path())

        if is_nuxt_proxy_path(request.path):
            from django_nuxt.proxy import proxy_nuxt_request

            return proxy_nuxt_request(request)

        return self.get_response(request)
