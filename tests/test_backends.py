from django.test import TestCase
from .driver import DjangoNuxtDriver
from grappa import should

class TestBackends(TestCase):
  def setUp(self):
    self.driver = DjangoNuxtDriver()

  def test_user_injection(self):
    self.driver.user(username="test")
    page = self.driver.getNuxtPage()
    page.should.contain("test")