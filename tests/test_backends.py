from django.test import TestCase
from .driver import DjangoNuxtDriver
from grappa import should

class TestBackends(TestCase):
  def setUp(self):
    self.driver = DjangoNuxtDriver(self)

  def test_page(self):
    response = self.driver.getNuxtPage()
    str(response.content) | should.contain("Hello test")

  def test_logged_in_user_injection(self):
    self.driver.user(username="test")
    django_nuxt = self.driver.getDjangoNuxt()
    django_nuxt["user"] | should.have.key("username").that.should.be.equal("test")
    django_nuxt["user"] | should.have.key("is_authenticated").that.should.be.equal(True)

  def test_logged_out_user_injection(self):
    django_nuxt = self.driver.getDjangoNuxt()
    django_nuxt["user"] | should.have.key("is_authenticated").that.should.be.equal(False)

  def test_data_processors(self):
    self.driver.data_processor(lambda context, request: {"test_key": "test_value"})
    django_nuxt = self.driver.getDjangoNuxt()
    django_nuxt | should.have.key("test_key").that.should.be.equal("test_value")