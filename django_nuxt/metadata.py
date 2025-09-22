from rest_framework.metadata import SimpleMetadata
from rest_framework.relations import ManyRelatedField
from .standard_schema import convert_to_standard_schema_v1

class NuxtSchemaMetadata(SimpleMetadata):
  def get_field_info(self, field):
    info = super().get_field_info(field)
    if field.write_only:
      info['write_only'] = True
    if field.initial:
      info['initial'] = field.initial
    if field.validators:
      info['validators'] = self.map_validators(field.validators)
    if isinstance(field, ManyRelatedField):
      info['type'] = 'many related'
      # Don't do this like this, will leak data! Apply permissions, at least.
      #info['choices'] = [{'id': x.pk, 'label': str(x)} for x in list(field.child_relation.queryset.all())]
    return info

  def determine_metadata(self, request, view):
    if not hasattr(view, 'get_serializer'):
      return None
    serializer = view.get_serializer()
    metadata = self.get_serializer_info(serializer)
    
    metadata["~standard"] = convert_to_standard_schema_v1(metadata)
    metadata["~metadata"] = super().determine_metadata(request, view)
    return metadata

  def map_validators(self, validators):
    validators_map = [] 
    for validator in validators:
      if validator.__class__.__name__ == "RegexValidator":
        validators_map.append({
          "name": "RegexValidator",
          "regex": validator.regex.pattern,
          "message": validator.message
        })
    return validators_map