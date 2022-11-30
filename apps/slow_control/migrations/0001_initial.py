# Generated by Django 3.2.12 on 2022-11-30 10:18

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('deviceOptions', models.JSONField(null=True)),
                ('isOnline', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='RunConfig',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=500)),
                ('lastSaved', models.DateTimeField(auto_now=True)),
                ('lastLoaded', models.DateTimeField(null=True)),
                ('priority', models.IntegerField(default=0)),
                ('totalTime', models.FloatField(default=0)),
                ('runConfigStatus', models.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RunConfigStep',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=1000)),
                ('deviceName', models.CharField(max_length=500)),
                ('deviceOptions', models.JSONField(null=True)),
                ('time', models.IntegerField()),
                ('runconfig', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slow_control.runconfig')),
            ],
            options={
                'ordering': ['time'],
            },
        ),
    ]
