from django.apps import AppConfig


class DjangoNuxtConfig(AppConfig):
    name = "django_nuxt"
    verbose_name = "Django Nuxt"
    default = True

    def ready(self):
        from django_nuxt.conf import get_nuxt_dev_server_url
        from django_nuxt.proxy import patch_wsgi_websocket_proxy

        # Dev-only: tunnel Vite/DevTools WebSocket upgrades to the Nuxt server.
        if get_nuxt_dev_server_url():
            patch_wsgi_websocket_proxy()
