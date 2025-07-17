from rest_framework.metadata import SimpleMetadata

class NuxtSchemaMetadata(SimpleMetadata):
  def get_field_info(self, field):
    info = super().get_field_info(field)
    if field.write_only:
      info['write_only'] = True
    if field.initial:
      info['initial'] = field.initial
    return info

  def determine_metadata(self, request, view):
    serializer = view.get_serializer()
    metadata = self.get_serializer_info(serializer)
    
    metadata["~metadata"] = super().determine_metadata(request, view)
    return metadata