from rest_framework import routers, serializers, viewsets, filters
from .models import Todo

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

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', ]

router = routers.DefaultRouter()
router.register(r'todo', TodoViewSet)

urlpatterns = router.urls