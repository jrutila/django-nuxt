from django.apps import AppConfig


class DjangoNuxtConfig(AppConfig):
    name = "django_nuxt"
    verbose_name = "Django Nuxt"
    default = True

    def ready(self):
        from django_nuxt.conf import get_nuxt_dev_server_url
        from django_nuxt.middleware import install_asset_proxy_middleware
        from django_nuxt.proxy import patch_wsgi_websocket_proxy

        if get_nuxt_dev_server_url():
            install_asset_proxy_middleware()
            patch_wsgi_websocket_proxy()
