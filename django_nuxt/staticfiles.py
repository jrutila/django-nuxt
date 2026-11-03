import os
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage


class NuxtStaticFilesFinder(FileSystemFinder):
    """Collect Nuxt build output and the Nuxt public folder.

    Every directory in ``DJANGO_NUXT_GENERATED_FOLDER`` is copied to
    ``STATIC_ROOT`` under that directory's name (``_nuxt``, ``_fonts``, and
    the rest). A directory named like the first segment of ``STATIC_URL``
    (usually ``static``) is collected without that name, so ``static/_nuxt``
    is served at ``/static/_nuxt`` and ``static/_fonts`` at ``/static/_fonts``.
    Files in the generated folder itself,
    such as ``200.html``, are not collected.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        generated = getattr(settings, "DJANGO_NUXT_GENERATED_FOLDER", "ui/.output/public/")
        public = getattr(settings, "DJANGO_NUXT_PUBLIC_FOLDER", "ui/public/")
        static_name = _static_directory_name()
        self.locations = [
            ("" if static_name and name == static_name else name, os.path.join(generated, name))
            for name in _child_directories(generated)
        ]
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


def _child_directories(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(
        name
        for name in os.listdir(folder)
        if os.path.isdir(os.path.join(folder, name))
    )
