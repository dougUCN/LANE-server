# Generated by Django 3.2.12 on 2022-06-03 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('states', models.TextField(blank=True)),
                ('currentState', models.TextField(blank=True)),
                ('isOnline', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Runfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('qOrder', models.IntegerField()),
                ('startTime', models.DateTimeField(null=True)),
                ('deviceStates', models.JSONField(null=True)),
                ('runTime', models.FloatField(default=0)),
                ('submitted', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(blank=True, max_length=100)),
            ],
        ),
    ]
