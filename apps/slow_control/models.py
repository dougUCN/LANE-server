from django.db import models


class RunConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)
    lastSaved = models.DateTimeField(null=True)
    lastLoaded = models.DateTimeField(null=True)
    priority = models.IntegerField(default=0)
    totalTime = models.FloatField(default=0)
    steps = models.JSONField(null=True)
    status = models.CharField(blank=True, max_length=100)


class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    deviceOptions = models.JSONField(null=True)
    isOnline = models.BooleanField()
