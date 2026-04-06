from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Todo(models.Model):
  title = models.CharField(max_length=200, validators=[
    RegexValidator(
        regex=fr'^td: \d{2}',
        message='Title must start with "td: <two-digit-number>"'
    )
  ])
  done = models.DateTimeField(null=True, blank=True)

class Who(models.Model):
  name = models.CharField(max_length=200)

  todos = models.ManyToManyField(Todo, blank=True, null=True, related_name='whos')