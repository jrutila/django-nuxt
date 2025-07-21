from django_nuxt.metadata import NuxtSchemaMetadata

class TodoMetadata(NuxtSchemaMetadata):
  def determine_metadata(self, request, view):
    return super().determine_metadata(request, view)