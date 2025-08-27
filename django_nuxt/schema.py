from rest_framework.schemas.generators import BaseSchemaGenerator
from django.conf import settings
from django.utils.module_loading import import_string

class NuxtSchemaGenerator(BaseSchemaGenerator):
  def get_schema(self, context=None, request=None, ignore_request=False):
    self._initialise_endpoints()
    _, view_endpoints = self._get_paths_and_endpoints(request if not ignore_request else None)
    models = {}
    # Find the POST or GET endpoint for each model
    for view in view_endpoints:
      basename = getattr(view[2], "basename", None)
      if not basename:
        continue
      action = getattr(view[2], "action", None)
      if action not in ["list", "create"]:
        continue
      if basename not in models:
        models[basename] = {}
      if getattr(models[basename], "action", None) == "POST":
        continue
      models[basename] = view

    generals = {}
    for model, view in models.items():
      metadata = self._convert_to_nuxt_metadata(view)
      if not metadata:
        continue
      metadata["~metadata"]["model"] = model
      generals[model] = metadata
    return generals

  def _convert_to_nuxt_metadata(self, view):
    default_metadata = getattr(settings, 'DJANGO_NUXT_DEFAULT_METADATA_CLASS', None)
    if not default_metadata:
      default_metadata = getattr(settings, 'REST_FRAMEWORK', {}).get('DEFAULT_METADATA_CLASS', None)
    if not default_metadata:
      default_metadata = 'django_nuxt.metadata.NuxtSchemaMetadata'
    md = import_string(default_metadata)()
    return md.determine_metadata(None, view[2])
