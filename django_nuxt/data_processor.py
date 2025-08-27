from django.conf import settings
from django.utils.module_loading import import_string

def nuxt_schema_data_processor(context, request):
  schema_key = getattr(settings, "DJANGO_NUXT_SCHEMA_KEY", "schema")
  schema_generator = getattr(settings, "DJANGO_NUXT_SCHEMA_GENERATOR", 'django_nuxt.schema.NuxtSchemaGenerator')
  nuxt_django_prefix = getattr(settings, 'DJANGO_NUXT_PREFIX', 'NUXT_DJANGO_')
  generator = import_string(schema_generator)()
  context[f'{nuxt_django_prefix}SCHEMA_KEY'] = schema_key

  schema = generator.get_schema(context, request, ignore_request=True)
  return {
    schema_key: schema,
    "_scripts": [f'''
    <script>
      for (const schema of Object.values(window.django_nuxt.{schema_key})) {{
        if (schema['~standard']) {{
          schema['~standard'].validate = new Function('value', schema['~standard'].validate);
        }}
      }}
    </script>
''']
  }