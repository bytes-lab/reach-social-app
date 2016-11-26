# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('circles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatContacts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('favourite_type', models.PositiveIntegerField(default=0)),
                ('otheruser', models.ForeignKey(related_name='chatcontacts_otherusers', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='chatcontacts_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContactReq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('req_type', models.PositiveIntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('otheruser', models.ForeignKey(related_name='contactreq_otherusers', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='contactreq_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alert_type', models.PositiveIntegerField(default=0)),
                ('reading_type', models.PositiveIntegerField(default=0)),
                ('alert', models.CharField(max_length=255, blank=True)),
                ('sound', models.CharField(max_length=50, blank=True)),
                ('category', models.CharField(max_length=50, blank=True)),
                ('custom', models.TextField()),
                ('fromuser', models.ForeignKey(related_name='pushnotification_fromusers', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='pushnotification_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(default=b'Like', max_length=255, choices=[(b'Like', b'Like'), (b'Feedback', b'Feedback'), (b'PostComment', b'PostComment'), (b'TopicComment', b'TopicComment'), (b'Request', b'Request')])),
                ('read', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('action_user', models.ForeignKey(related_name='action_user', to=settings.AUTH_USER_MODEL)),
                ('like', models.ForeignKey(blank=True, to='posts.Like', null=True)),
                ('post_comment', models.ForeignKey(blank=True, to='posts.Comment', null=True)),
                ('topic_comment', models.ForeignKey(blank=True, to='circles.TopicComment', null=True)),
                ('user', models.ForeignKey(related_name='feed_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfinityBan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_unique_id', models.CharField(max_length=500)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_token', models.TextField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=255, blank=True)),
                ('biography', models.TextField(blank=True)),
                ('like_count', models.PositiveIntegerField(default=0)),
                ('comment_count', models.PositiveIntegerField(default=0)),
                ('rate', models.PositiveIntegerField(default=0)),
                ('count_rates', models.PositiveIntegerField(default=0)),
                ('avatar', models.FileField(default=b'/media/default_images/default.png', upload_to=utils.get_file_path)),
                ('is_facebook', models.BooleanField(default=False)),
                ('is_twitter', models.BooleanField(default=False)),
                ('is_instagram', models.BooleanField(default=False)),
                ('facebook_url', models.CharField(max_length=500, blank=True)),
                ('twitter_url', models.CharField(max_length=500, blank=True)),
                ('instagram_url', models.CharField(max_length=500, blank=True)),
                ('device_unique_id', models.CharField(max_length=500)),
                ('country_name', models.CharField(max_length=30, blank=True)),
                ('city_name', models.CharField(max_length=30, blank=True)),
                ('latitude', models.FloatField(default=-90)),
                ('longitude', models.FloatField(default=-90)),
                ('qbchat_id', models.IntegerField(default=0)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, dim=3)),
                ('user', models.OneToOneField(related_name='info', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.IntegerField(default=1)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('message', models.CharField(max_length=255)),
                ('receiver', models.ForeignKey(related_name='receiver_rate', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(related_name='sender_rate', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('reported', models.ForeignKey(related_name='reported_user', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='who_report_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allow', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('request_user', models.ForeignKey(related_name='request_user', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='userfeed',
            name='user_rate',
            field=models.ForeignKey(blank=True, to='users.UserRate', null=True),
        ),
        migrations.AddField(
            model_name='userfeed',
            name='user_request',
            field=models.ForeignKey(blank=True, to='users.UserRequest', null=True),
        ),
    ]
