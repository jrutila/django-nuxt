from django.conf import settings

from django_nuxt.conf import get_nuxt_dev_server_url

ASSET_MIDDLEWARE = "django_nuxt.middleware.NuxtAssetProxyMiddleware"

NUXT_ASSET_PREFIXES = (
    "/_nuxt/",
    "/__nuxt_devtools__/",
    "/_fonts/",
    "/fonts/",
)
NUXT_ASSET_EXACT = (
    "/_nuxt",
    "/__nuxt_devtools__",
    "/_fonts",
    "/fonts",
)


def is_nuxt_asset_path(path):
    return path in NUXT_ASSET_EXACT or path.startswith(NUXT_ASSET_PREFIXES)


def install_asset_proxy_middleware():
    """Put the asset proxy first so session/auth never run for Vite files."""
    middleware = list(settings.MIDDLEWARE)
    if ASSET_MIDDLEWARE not in middleware:
        settings.MIDDLEWARE = [ASSET_MIDDLEWARE, *middleware]


class NuxtAssetProxyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if get_nuxt_dev_server_url() and is_nuxt_asset_path(request.path):
            from django_nuxt.proxy import proxy_nuxt_request

            return proxy_nuxt_request(request)
        return self.get_response(request)
