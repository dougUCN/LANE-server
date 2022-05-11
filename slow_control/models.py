from django.db import models

class Runfile(models.Model):
    name = models.CharField(max_length=500)
    qOrder = models.IntegerField()
    startTime = models.DateTimeField(null=True)
    deviceStates = models.JSONField(null=True)
    runTime = models.FloatField(default = 0)
    submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(blank=True, max_length=100)

class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    states = models.TextField(blank=True)
    currentState = models.TextField(blank=True)
    isOnline = models.BooleanField()