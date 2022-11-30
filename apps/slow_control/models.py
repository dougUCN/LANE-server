from django.db import models
import uuid


class RunConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)
    lastSaved = models.DateTimeField(auto_now=True)
    lastLoaded = models.DateTimeField(null=True)
    priority = models.IntegerField(default=0)
    totalTime = models.FloatField(default=0)
    runConfigStatus = models.JSONField(null=True)


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
    RunConfig = models.ForeignKey(
        RunConfig,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['time']


class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    deviceOptions = models.JSONField(null=True)
    isOnline = models.BooleanField()
