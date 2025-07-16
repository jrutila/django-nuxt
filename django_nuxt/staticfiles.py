from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from django.conf import settings

nuxt_generated_folder = getattr(settings, 'DJANGO_NUXT_GENERATED_FOLDER', 'ui/.output/public/')
nuxt_public_folder = getattr(settings, 'DJANGO_NUXT_PUBLIC_FOLDER', 'ui/public/')

class NuxtStaticFilesFinder(FileSystemFinder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locations = [
            ('_nuxt', f'{nuxt_generated_folder}_nuxt'),
            ('', nuxt_public_folder),
        ]
        for prefix, root in self.locations:
            filesystem_storage = FileSystemStorage(location=root)
            filesystem_storage.prefix = prefix
            self.storages[root] = filesystem_storage