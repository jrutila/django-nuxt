from rest_framework import routers, serializers, viewsets
from .models import Todo

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = '__all__'

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

router = routers.DefaultRouter()
router.register(r'todos', TodoViewSet)

urlpatterns = router.urls