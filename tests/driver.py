from django.test import RequestFactory
from django.contrib.auth.models import User
from django_nuxt.views import nuxt_proxy

class DjangoNuxtDriver:
  def __init__(self):
    self.factory = RequestFactory()

  def user(self, **kwargs):
    self.user = User.objects.create(**kwargs)
    return self

  def getNuxtPage(self):
    request = self.factory.get("/")
    request.user = self.user
    request.session = {}
    request.session["_auth_user_id"] = self.user.id
    response = nuxt_proxy(request)
    return response