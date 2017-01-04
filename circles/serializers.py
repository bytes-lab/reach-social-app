from rest_framework import serializers

from circles.models import Circle, UserCircle, Topic, Group, TopicComment, Notification
from users.models import UserReport
from users.serializers import UserSerializer
from django.contrib.auth.models import User


class TopicCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    date = serializers.SerializerMethodField("get_format_date")

    def get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    class Meta:
        model = TopicComment
        fields = ("id", "author", "text", "permission", "date")


class NotificationSerializer(serializers.ModelSerializer):
    otheruser = UserSerializer(read_only=True)
    date = serializers.SerializerMethodField("get_format_date")

    def get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %m/%d/%Y")

    class Meta:
        model = Notification
        fields = ("id", "user", "circle", "otheruser", "date", "detail", "notitype", "topic")


class TopicSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField("get_topic_replies")
    date = serializers.SerializerMethodField("get_format_date")

    def get_topic_replies(self, obj):
        # user_id = self.context.get("user_id")
        # reported_users = UserReport.objects.filter(user_id=user_id).values_list('reported_id', flat=True)
        replies = TopicComment.objects.filter(topic=obj)

        return TopicCommentSerializer(replies, many=True).data

    def get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    class Meta:
        model = Topic
        fields = ("id", "author", "text", "permission", "date", "replies")


class GroupSerializer(serializers.ModelSerializer):
    count_circles = serializers.SerializerMethodField("get_number_circles")

    def get_number_circles(self, obj):
        return Circle.objects.filter(group=obj).count()

    class Meta:
        model = Group
        fields = ("id", "name", "count_circles")


class CircleSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField("count_members")
    join = serializers.SerializerMethodField("check_join")
    group = GroupSerializer(read_only=True)

    def count_members(self, obj):
        count = UserCircle.objects.filter(circle=obj).count()
        return count

    def check_join(self, obj):
        check = False
        user_id = self.context.get("user_id")
        if UserCircle.objects.filter(circle=obj, user_id=user_id).exists():
            check = True
        return check

    class Meta:
        model = Circle
        fields = ("id", "name", "owner", "description", "permission", "image", "group", "members_count", "join")


class FullCircleSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField("count_members")
    members = serializers.SerializerMethodField("members_list")
    join = serializers.SerializerMethodField("check_join")
    group = GroupSerializer(read_only=True)
    topics = serializers.SerializerMethodField("get_circle_topics")

    def members_list(self, obj):
        user_ids = [item.user_id for item in UserCircle.objects.filter(circle=obj)]
        users = User.objects.filter(id__in=user_ids)
        return UserSerializer(users, many=True).data

    def count_members(self, obj):
        return UserCircle.objects.filter(circle=obj).count()

    def get_circle_topics(self, obj):
        user_id = self.context.get("user_id")
        reported_users = UserReport.objects.filter(user_id=user_id).values_list('reported_id', flat=True)
        topics = Topic.objects.filter(circle=obj).exclude(author_id__in=reported_users)
        return TopicSerializer(topics, many=True).data

    def check_join(self, obj):
        user_id = self.context.get("user_id")
        return UserCircle.objects.filter(circle=obj, user_id=user_id).exists()

    class Meta:
        model = Circle
        fields = ("id", "name", "owner", "description", "permission", "image", "group", "members_count", "join",
                  "topics", "members")
