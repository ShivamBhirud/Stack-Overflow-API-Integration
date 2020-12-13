from django.db import models
from datetime import datetime

# Create your models here.
class Fields(models.Model):
    tag = models.CharField(max_length=100, blank=True, null=True)
    fromdate = models.DateField(default=datetime.now)
    todate = models.DateField(default=datetime.now)
    orderby = models.CharField(default='desc', max_length=4)
    counter = models.IntegerField(default=0)
    q = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.tag

class Cached_Data(models.Model):
    fields = models.ForeignKey(Fields, on_delete=models.CASCADE,
        related_name='cached')
    title = models.CharField(max_length=1000, blank=True, null=True)
    link = models.URLField(default='')
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.title


