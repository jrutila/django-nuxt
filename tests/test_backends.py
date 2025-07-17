from django.test import TestCase
from .driver import DjangoNuxtDriver
from grappa import should

class TestBackends(TestCase):
  def setUp(self):
    self.driver = DjangoNuxtDriver()

  def test_logged_in_user_injection(self):
    self.driver.user(username="test")
    django_nuxt = self.driver.getDjangoNuxt()
    django_nuxt["user"] | should.have.key("username").that.should.be.equal("test")
    django_nuxt["user"] | should.have.key("is_authenticated").that.should.be.equal(True)

  def test_logged_out_user_injection(self):
    django_nuxt = self.driver.getDjangoNuxt()
    django_nuxt["user"] | should.have.key("is_authenticated").that.should.be.equal(False)