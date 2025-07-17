from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django_nuxt.urls import NuxtStaticUrls, NuxtCatchAllUrls
from grappa import should
import json

urlpatterns = [] + NuxtStaticUrls() + NuxtCatchAllUrls()

class DjangoNuxtDriver:
  def __init__(self, test_case):
    self.test_case = test_case
    self.data_processors = []
    self.current_user = None

  def user(self, **kwargs):
    self.current_user = User.objects.create(**kwargs)
    return self

  def data_processor(self, func):
    self.data_processors.append(func)
    return self

  def getNuxtPage(self):
    with self.test_case.settings(DJANGO_NUXT_DATA_PROCESSORS=self._get_processors()):
      client = Client()
      if self.current_user:
        client.force_login(self.current_user)
      response = client.get("/")
      str(response.content) | should.contain("Hello test")
    return response

  def getDjangoNuxt(self):
    with self.test_case.settings(DJANGO_NUXT_DATA_PROCESSORS=self._get_processors()):
      client = Client()
      if self.current_user:
        client.force_login(self.current_user)

      response = client.get("/")
      html = str(response.content)
      django_nuxt = html.split("window.django_nuxt = ")[1].split("</script>")[0]
    return json.loads(django_nuxt)

  def _get_processors(self):
    processors = []
    for func in self.data_processors:
      # For test purposes, we need to make the processor importable by string.
      # We'll register it on a unique module path.
      import types, sys, uuid
      module_name = f"tests._proc_{uuid.uuid4().hex}"
      mod = types.ModuleType(module_name)
      func_name = f"proc"
      setattr(mod, func_name, func)
      sys.modules[module_name] = mod
      processors.append(f"{module_name}.{func_name}")
    return processors