from django.core.management.base import BaseCommand
from django_nuxt.schema import NuxtSchemaGenerator

class Command(BaseCommand):
    help = "Generate Nuxt schema"

    def handle(self, *args, **options):
      generator = NuxtSchemaGenerator()
      print(generator.get_schema())