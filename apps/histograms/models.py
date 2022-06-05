from django.db import models


class Histogram(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    name = models.CharField(blank=True, max_length=500)
    data = models.JSONField(null=True)
    xrange = models.JSONField(null=True)
    yrange = models.JSONField(null=True)
    len = models.PositiveBigIntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(blank=True, max_length=100)


class HistTable(models.Model):
    name = models.CharField(max_length=500, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    histIDs = models.JSONField(null=True)
    isLive = models.BooleanField()
