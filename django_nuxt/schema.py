from rest_framework.schemas.generators import BaseSchemaGenerator
from django_nuxt.metadata import NuxtSchemaMetadata

class NuxtSchemaGenerator(BaseSchemaGenerator):
  def get_schema(self, request=None, public=False):
    self._initialise_endpoints()
    _, view_endpoints = self._get_paths_and_endpoints(None if public else request)
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
      metadata["~metadata"]["model"] = model
      generals[model] = metadata
    return generals

  def _convert_to_nuxt_metadata(self, view):
    md = NuxtSchemaMetadata()
    return md.determine_metadata(None, view[2])
