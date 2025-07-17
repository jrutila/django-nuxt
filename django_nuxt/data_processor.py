from django_nuxt.schema import NuxtSchemaGenerator
from django.conf import settings

def nuxt_schema_data_processor(context, request):
  schema_key = getattr(settings, "DJANGO_NUXT_SCHEMA_KEY", "schema")
  nuxt_django_prefix = getattr(settings, 'DJANGO_NUXT_PREFIX', 'NUXT_DJANGO_')
  generator = NuxtSchemaGenerator()
  schema = generator.get_schema()
  context[f'{nuxt_django_prefix}SCHEMA_KEY'] = schema_key
  return {
    schema_key: schema,
  }