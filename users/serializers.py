from django.contrib.auth.models import User

from rest_framework import serializers

from users.models import UserProfile, UserReport, UserFeed, UserRate, UserRequest, ChatContacts, ContactReq, PushNotification
from posts.models import CommentLike, Comment, Like

import json

class UserProfileSerializer(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField("get_user_rate")

    def get_user_rate(self, obj):
        if obj.rate != 0:
            return obj.rate / obj.count_rates
        return 0

    class Meta:
        model = UserProfile
        fields = ("full_name", "biography", "like_count", "comment_count", "rate", "avatar", "is_facebook",
                  "is_twitter", "is_instagram", "facebook_url", "twitter_url", "instagram_url", "country_name", "city_name", "latitude", "longitude","qbchat_id")


class UserSerializer(serializers.ModelSerializer):
    info = UserProfileSerializer(read_only=True)
    count_downvoted = serializers.SerializerMethodField("get_user_count_downvoted")
    count_upvoted = serializers.SerializerMethodField("get_user_count_upvoted")
    count_likes = serializers.SerializerMethodField("get_user_count_likes")
    count_comments = serializers.SerializerMethodField("get_user_count_comments")
    complete_likes = serializers.SerializerMethodField("get_user_complete_likes")

    def get_user_count_downvoted(self, obj):
        return CommentLike.objects.filter(statement=False, comment__author=obj).count()

    def get_user_count_upvoted(self, obj):
        return CommentLike.objects.filter(statement=True, comment__author=obj).count()

    def get_user_count_likes(self, obj):
        return Like.objects.filter(post__author=obj).count()

    def get_user_count_likes(self, obj):
        return Like.objects.filter(post__author=obj).count()

    def get_user_count_comments(self, obj):
        return Comment.objects.filter(author=obj).count()

    def get_user_complete_likes(self, obj):
        all_count = CommentLike.objects.filter(comment__author=obj).count()
        if all_count == 0:
            all_count += 1
        positive_count = CommentLike.objects.filter(statement=True, comment__author=obj).count()
        return (positive_count * 100) / all_count

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "info", "count_downvoted", "count_upvoted",
                  "count_likes", "count_comments", "complete_likes")


class ChatContactsSerializer(serializers.ModelSerializer):
    otheruser = UserSerializer(read_only=True)

    class Meta:
        model = ChatContacts
        fields = ("id",  "user",  "otheruser", "favourite_type" )


class PushNotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    fromuser = UserSerializer(read_only=True)

    class Meta:
        model = PushNotification
        fields = ("user", "fromuser", "alert_type", "reading_type", "alert", 
            "sound", "category", "custom")


class ContactReqSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    date = serializers.SerializerMethodField("_get_format_date")

    def _get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    class Meta:
        model = ContactReq
        fields = ("id", "user", "otheruser", "req_type", "date")


class UserReportSerializer(serializers.ModelSerializer):
    reported = UserSerializer(read_only=True)
    date = serializers.SerializerMethodField("_get_format_date")

    def _get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    class Meta:
        model = UserReport
        fields = ("id", "reported", "date")


class UserRateSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    date = serializers.SerializerMethodField("_get_format_date")

    def _get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    class Meta:
        model = UserRate
        fields = ("id", "sender", "receiver", "rate", "date", "message")


class UserRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    date = serializers.SerializerMethodField("_get_format_date")

    def _get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    class Meta:
        model = UserRequest
        fields = ('id', 'user', 'allow', 'date')


class UserFeedSerializer(serializers.ModelSerializer):
    action_user = UserSerializer(read_only=True)
    object = serializers.SerializerMethodField('_get_feed_object')
    date = serializers.SerializerMethodField("_get_format_date")

    def _get_feed_object(self, obj):
        from posts.serializers import PostSerializer
        from circles.serializers import TopicSerializer

        if obj.like and obj.action == "Like":
            return PostSerializer(obj.like.post).data
        elif obj.post_comment and obj.action == "PostComment":
            return PostSerializer(obj.post_comment.post).data
        elif obj.topic_comment and obj.action == "TopicComment":
            return TopicSerializer(obj.topic_comment.topic).data
        elif obj.user_rate and obj.action == "Feedback":
            return UserRateSerializer(obj.user_rate).data
        elif obj.user_request and obj.action == "Request":
            return UserRequestSerializer(obj.user_request).data
        else:
            return 0

    def _get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    class Meta:
        model = UserFeed
        fields = ("id", "action_user", "action", "object", "date")
