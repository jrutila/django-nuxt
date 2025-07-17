from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django_nuxt.urls import NuxtStaticUrls, NuxtCatchAllUrls
from grappa import should
import json

urlpatterns = [] + NuxtStaticUrls() + NuxtCatchAllUrls()

class DjangoNuxtDriver:
  current_user = None

  def __init__(self):
    self.factory = RequestFactory()

  def user(self, **kwargs):
    self.current_user = User.objects.create(**kwargs)
    return self

  def getNuxtPage(self):
    client = Client()
    if self.current_user:
      client.force_login(self.current_user)
    response = client.get("/")
    str(response.content) | should.contain("Hello test")
    return response

  def getDjangoNuxt(self):
    client = Client()
    if self.current_user:
      client.force_login(self.current_user)
    response = client.get("/")
    html = str(response.content)
    django_nuxt = html.split("window.django_nuxt = ")[1].split("</script>")[0]
    return json.loads(django_nuxt)