from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import *

from circles.models import TopicComment
from posts.models import Comment, Like
from utils import get_file_path


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="info")
    full_name = models.CharField(max_length=255, blank=True)
    biography = models.TextField(blank=True)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    rate = models.PositiveIntegerField(default=0)
    count_rates = models.PositiveIntegerField(default=0)
    avatar = models.FileField(upload_to=get_file_path, 
        default="/media/default_images/default.png")
    is_facebook = models.BooleanField(default=False)
    is_twitter = models.BooleanField(default=False)
    is_instagram = models.BooleanField(default=False)
    facebook_url = models.CharField(max_length=500, blank=True)
    twitter_url = models.CharField(max_length=500, blank=True)
    instagram_url = models.CharField(max_length=500, blank=True)
    device_unique_id = models.CharField(max_length=500)
    country_name = models.CharField(max_length=30, blank=True)
    state_name = models.CharField(max_length=30, blank=True)
    city_name = models.CharField(max_length=30, blank=True)
    latitude = models.FloatField(default=-90)
    longitude = models.FloatField(default=-90)
    qbchat_id = models.IntegerField(default=0)
    location = models.PointField(srid=4326, dim=3, blank=True, null=True)
    objects = models.GeoManager()

    # def save(self, **kwargs):
    #     point = "POINT(0 0)"
    #     self.location = fromstr(point)
    #     super(UserProfile, self).save()        

    def __unicode__(self):
        return self.user.username
        

class UserNotification(models.Model):
    user = models.ForeignKey(User)
    device_token = models.TextField()

    def __unicode__(self):
        return self.device_token


class ChatContacts(models.Model):
    user = models.ForeignKey(User, related_name='chatcontacts_users')
    otheruser = models.ForeignKey(User, related_name='chatcontacts_otherusers')
    favourite_type = models.PositiveIntegerField(default=0)


class ContactReq(models.Model):
    user = models.ForeignKey(User, related_name='contactreq_users')
    otheruser = models.ForeignKey(User, related_name='contactreq_otherusers')
    req_type = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{} - {}".format(self.user, self.otheruser)


class PushNotification(models.Model):
    user = models.ForeignKey(User, related_name='pushnotification_users')
    fromuser = models.ForeignKey(User, related_name='pushnotification_fromusers')
    alert_type = models.PositiveIntegerField(default=0)
    reading_type = models.PositiveIntegerField(default=0)
    alert = models.CharField(max_length=255, blank=True)
    sound = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=50, blank=True)
    custom = models.TextField()

    def __unicode__(self):
        return "{} - {}".format(self.fromuser, self.user)


class UserRate(models.Model):
    sender = models.ForeignKey(User, related_name="sender_rate")
    receiver = models.ForeignKey(User, related_name="receiver_rate")
    rate = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=255)

    def __unicode__(self):
        return self.sender.username


class UserReport(models.Model):
    user = models.ForeignKey(User, related_name="who_report_user")
    reported = models.ForeignKey(User, related_name="reported_user")
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{} report {} on {}'.format(self.user.username, self.reported.username, self.date)


class UserRequest(models.Model):
    user = models.ForeignKey(User)
    request_user = models.ForeignKey(User, related_name="request_user")
    allow = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{} to {} [{}] {}'.format(self.user.username,
                                         self.request_user.username,
                                         self.allow,
                                         self.date)


class UserFeed(models.Model):
    ACTION_CHOICES = (
        ('Like', 'Like'),
        ('Feedback', 'Feedback'),
        ('PostComment', 'PostComment'),
        ('TopicComment', 'TopicComment'),
        ('Request', 'Request'),
    )
    user = models.ForeignKey(User, related_name="feed_user")
    action_user = models.ForeignKey(User, related_name="action_user")
    like = models.ForeignKey(Like, blank=True, null=True)
    post_comment = models.ForeignKey(Comment, blank=True, null=True)
    topic_comment = models.ForeignKey(TopicComment, blank=True, null=True)
    user_rate = models.ForeignKey(UserRate, blank=True, null=True)
    user_request = models.ForeignKey(UserRequest, blank=True, null=True)
    action = models.CharField(max_length=255, choices=ACTION_CHOICES, default='Like')
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '[{}] - {}, {}, {}'.format(self.user.username,
                                          self.action_user.username,
                                          self.action,
                                          self.date)


class UserInfinityBan(models.Model):
    user = models.ForeignKey(User)
    device_unique_id = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{} - {}'.format(self.user.username,
                                self.device_unique_id)
