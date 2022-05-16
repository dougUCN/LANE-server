from django.db import models
from django.core.validators import int_list_validator


class Histogram(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    name = models.CharField(blank=True, max_length=500)
    x = models.TextField(blank=True, validators=[int_list_validator]) 
    y = models.TextField(blank=True, validators=[int_list_validator]) 
    len = models.PositiveBigIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(blank=True, max_length=100)
