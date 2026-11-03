import os
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage


class NuxtStaticFilesFinder(FileSystemFinder):
    """Collect Nuxt build output and the Nuxt public folder.

    Only the directory in ``DJANGO_NUXT_GENERATED_FOLDER`` named like the
    first segment of ``STATIC_URL`` (usually ``static``) is collected, and
    without that name, so ``static/_nuxt`` is served at ``/static/_nuxt`` and
    ``static/_fonts`` at ``/static/_fonts``. Other generated directories and
    files such as ``200.html`` are not collected. The Nuxt public folder is
    collected as it is.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        generated = getattr(settings, "DJANGO_NUXT_GENERATED_FOLDER", "ui/.output/public/")
        public = getattr(settings, "DJANGO_NUXT_PUBLIC_FOLDER", "ui/public/")
        static_name = _static_directory_name()
        static_root = os.path.join(generated, static_name) if static_name else ""
        self.locations = []
        if static_root and os.path.isdir(static_root):
            self.locations.append(("", static_root))
        self.locations.append(("", public))
        self.storages = {}
        for prefix, root in self.locations:
            storage = FileSystemStorage(location=root)
            storage.prefix = prefix
            self.storages[root] = storage


def _static_directory_name():
    """First path segment of STATIC_URL, ignoring a CDN host."""
    url = getattr(settings, "STATIC_URL", None) or ""
    path = urlparse(url).path if "://" in url else url
    parts = [part for part in path.split("/") if part]
    return parts[0] if parts else ""

