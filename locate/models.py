from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import *


class Groups(models.Model):
    creator = models.ForeignKey(User, related_name='groups_creators')
    group_title = models.TextField(blank=True)
    group_bio = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.creator.username
    