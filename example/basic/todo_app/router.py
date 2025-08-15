from rest_framework import routers, serializers, viewsets, filters
from .models import Todo, Who

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = '__all__'

    def validate_title(self, value):
        if value == "td: jep":
            raise serializers.ValidationError("Don't create todo named 'jep'")
        return value

    def validate(self, attrs):
        if attrs.get("title") and attrs.get("title").startswith("td: todo"):
            raise serializers.ValidationError("Don't create todo named 'todo'")
        return attrs
    
class WhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Who
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs.get('context', {}).get('request')
        if 'only_undone' in getattr(request, 'GET', {}):
            self.fields['todos'] = serializers.PrimaryKeyRelatedField(queryset=Todo.objects.filter(done__isnull=True), many=True)
        super().__init__(*args, **kwargs)

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', ]

class WhoViewSet(viewsets.ModelViewSet):
    queryset = Who.objects.all()
    serializer_class = WhoSerializer

router = routers.DefaultRouter()
router.register(r'todo', TodoViewSet)
router.register(r'who', WhoViewSet)

urlpatterns = router.urls