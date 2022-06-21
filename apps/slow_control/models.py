from django.db import models


class Runfile(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    name = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    lastLoaded = models.DateTimeField(null=True)
    priority = models.IntegerField()
    totalTime = models.FloatField(default=0)
    steps = models.JSONField(null=True)
    status = models.CharField(blank=True, max_length=100)


class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    deviceOptions = models.JSONField(null=True)
    isOnline = models.BooleanField()
