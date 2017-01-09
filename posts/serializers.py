from rest_framework import serializers

from posts.models import Post, PostHashtag, Comment, Like, CommentLike
from users.serializers import UserSerializer


class PostHashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostHashtag
        fields = ("id", "hashtag")


class PostCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_upvoted = serializers.SerializerMethodField("check_upvoted")
    is_downvoted = serializers.SerializerMethodField("check_downvoted")
    date = serializers.SerializerMethodField("get_format_date")

    def get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    def check_upvoted(self, obj):
        status = False
        user_id = self.context.get("user_id")
        if CommentLike.objects.filter(comment=obj, user_id=user_id, statement=True).exists():
            status = True
        return status

    def check_downvoted(self, obj):
        status = False
        user_id = self.context.get("user_id")
        if CommentLike.objects.filter(comment=obj, user_id=user_id, statement=False).exists():
            status = True
        return status

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "date", "permission", "rate", "is_upvoted", "is_downvoted", "best_response")


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post_hashtags = PostHashtagSerializer(many=True, read_only=True)
    post_comments = PostCommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField("get_post_comments")
    like_count = serializers.SerializerMethodField("get_post_likes")
    is_like = serializers.SerializerMethodField("check_user_like")
    date = serializers.SerializerMethodField("get_format_date")

    def get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    def check_user_like(self, obj):
        check = False
        user_id = self.context.get("user_id")
        if Like.objects.filter(post=obj, user=user_id).exists():
            check = True
        return check

    def get_post_comments(self, obj):
        count = Comment.objects.filter(post=obj).count()
        return count

    def get_post_likes(self, obj):
        # count = Like.objects.filter(post=obj).count()
        return obj.count_likes

    class Meta:
        model = Post
        fields = (
        "id", "author", "text", "date", "permission", "image", "video", "post_hashtags", "post_comments", "like_count",
        "comment_count", "is_like")


class PostSerializer_feed(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post_hashtags = PostHashtagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField("get_post_comments")
    like_count = serializers.SerializerMethodField("get_post_likes")
    is_like = serializers.SerializerMethodField("check_user_like")
    date = serializers.SerializerMethodField("get_format_date")
        
    def get_format_date(self, obj):
        return obj.date.strftime("%H:%M:%S %Y:%m:%d")

    def check_user_like(self, obj):
        check = False
        user_id = self.context.get("user_id")
        if Like.objects.filter(post=obj, user=user_id).exists():
            check = True
        return check

    def get_post_comments(self, obj):
        count = Comment.objects.filter(post=obj).count()
        return count

    def get_post_likes(self, obj):
        # count = Like.objects.filter(post=obj).count()
        return obj.count_likes

    class Meta:
        model = Post
        fields = (
        "id", "author", "text", "date", "permission", "image", "video", "post_hashtags", "post_comments", "like_count",
        "comment_count", "is_like")
