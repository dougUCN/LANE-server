from django.db import models
from .common import EnumState

class Runfile(models.Model):
    name = models.CharField(max_length=500)
    q_order = models.PositiveIntegerField(default=0)
    start_time = models.DateTimeField(null=True)
    device_states = models.JSONField(null=True)
    runtime = models.FloatField(default = 0)
    status = models.CharField(max_length=100, default=EnumState["QUEUED"])

class Device(models.Model):
    name = models.CharField(max_length=100)
    states = models.TextField()
    current_state = models.TextField()
    is_online = models.BooleanField(default = False)