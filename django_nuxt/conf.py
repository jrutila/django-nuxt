from django.conf import settings

DEFAULT_NUXT_DEV_SERVER = "http://localhost:3000"


def get_nuxt_dev_server_url():
    """
    Return the Nuxt development server URL when the reverse proxy should be used.

    Proxying is enabled when DJANGO_NUXT_SERVER_RUNNING is a URL or True, or when
    it is unset and DEBUG is True. It is disabled when the setting is False, or
    when it is unset and DEBUG is False.
    """
    nuxt_server_running = getattr(settings, "DJANGO_NUXT_SERVER_RUNNING", None)
    if nuxt_server_running or (settings.DEBUG and nuxt_server_running is None):
        if nuxt_server_running is True or nuxt_server_running is None:
            return DEFAULT_NUXT_DEV_SERVER
        return nuxt_server_running
    return None
