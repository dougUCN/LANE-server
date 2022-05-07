from django.db import models

# class Device(models.Model):
#     name = models.CharField(max_length=100)
#     states = models.TextField()
#     current_state = models.TextField()
#     is_online = models.BooleanField(default = False)

class Runfile(models.Model):
    name = models.CharField(max_length=500)
    q_order = models.PositiveIntegerField()
    start_time = models.DateTimeField(null=True)
    run = models.JSONField()
    runtime = models.FloatField(default = 0)
