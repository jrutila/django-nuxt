import os

from django.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage


class NuxtStaticFilesFinder(FileSystemFinder):
    """Collect Nuxt build output and the Nuxt public folder.

    Every directory in ``DJANGO_NUXT_GENERATED_FOLDER`` is copied to
    ``STATIC_ROOT`` under that directory's name (``_nuxt``, ``_fonts``, and
    the rest). Files in the generated folder itself, such as ``200.html``,
    are not collected.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        generated = getattr(settings, "DJANGO_NUXT_GENERATED_FOLDER", "ui/.output/public/")
        public = getattr(settings, "DJANGO_NUXT_PUBLIC_FOLDER", "ui/public/")
        self.locations = [
            (name, os.path.join(generated, name))
            for name in _child_directories(generated)
        ]
        self.locations.append(("", public))
        self.storages = {}
        for prefix, root in self.locations:
            storage = FileSystemStorage(location=root)
            storage.prefix = prefix
            self.storages[root] = storage


def _child_directories(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(
        name
        for name in os.listdir(folder)
        if os.path.isdir(os.path.join(folder, name))
    )
