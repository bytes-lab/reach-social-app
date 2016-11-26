# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Circle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.FileField(upload_to=utils.get_file_path, blank=True)),
                ('permission', models.BooleanField(default=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detail', models.CharField(max_length=70)),
                ('notitype', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('circle', models.ForeignKey(to='circles.Circle')),
                ('otheruser', models.ForeignKey(related_name='notification_otherusers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('permission', models.BooleanField(default=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('circle', models.ForeignKey(related_name='topics', to='circles.Circle')),
            ],
        ),
        migrations.CreateModel(
            name='TopicComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('permission', models.BooleanField(default=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(related_name='topiccomment_topics', to='circles.Topic')),
            ],
        ),
        migrations.CreateModel(
            name='UserCircle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('circle', models.ForeignKey(to='circles.Circle')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='notification',
            name='topic',
            field=models.ForeignKey(related_name='notification_topics', to='circles.Topic'),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(related_name='notification_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='circle',
            name='group',
            field=models.ForeignKey(to='circles.Group'),
        ),
        migrations.AddField(
            model_name='circle',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
