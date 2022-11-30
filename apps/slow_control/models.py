from django.db import models
import uuid


class RunConfigStep(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    description = models.CharField(max_length=1000)
    deviceName = models.CharField(max_length=500)
    deviceOptions = models.JSONField(null=True)
    time = models.IntegerField()

    class Meta:
        ordering = ['time']


class RunConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)
    lastSaved = models.DateTimeField(auto_now=True)
    lastLoaded = models.DateTimeField(null=True)
    priority = models.IntegerField(default=0)
    totalTime = models.FloatField(default=0)
    steps = models.ForeignKey(
        RunConfigStep,
        on_delete=models.CASCADE,
        null=True,
    )
    runConfigStatus = models.JSONField(null=True)


class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    deviceOptions = models.JSONField(null=True)
    isOnline = models.BooleanField()
