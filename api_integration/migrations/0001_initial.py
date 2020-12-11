# Generated by Django 3.1.4 on 2020-12-11 16:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fields',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(blank=True, max_length=100, null=True)),
                ('fromdate', models.DateField(default=datetime.datetime.now)),
                ('todate', models.DateField(default=datetime.datetime.now)),
                ('orderby', models.CharField(default='desc', max_length=4)),
                ('counter', models.IntegerField(default=0)),
            ],
        ),
    ]