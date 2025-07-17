from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
class Todo(models.Model):
  title = models.CharField(max_length=200, validators=[
    RegexValidator(
        regex=r'^td: ',
        message='Title must start with "td: "'
    )
  ])
  done = models.DateTimeField(null=True, blank=True)