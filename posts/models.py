from django.db import models
from django.contrib.auth.models import User

from utils import get_file_path


class Post(models.Model):
    author = models.ForeignKey(User, related_name="user")
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    permission = models.BooleanField(default=True)
    count_likes = models.IntegerField(default=0)
    image = models.FileField(upload_to=get_file_path, blank=True)
    video = models.FileField(upload_to=get_file_path, blank=True)

    def __unicode__(self):
        return "User: [%s], Text: [%s]" % (self.author.username,
                                           self.text[:30])


class PostHashtag(models.Model):
    hashtag = models.CharField(max_length=255)
    post = models.ForeignKey(Post, related_name="post_hashtags")

    def __unicode__(self):
        return "Hashtag: [%s], Post: [%s]" % (self.hashtag, self.post.text[:30])


class Comment(models.Model):
    author = models.ForeignKey(User)
    post = models.ForeignKey(Post, related_name="post_comments")
    text = models.TextField()
    rate = models.IntegerField(default=0)
    permission = models.BooleanField(default=True)
    best_response = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "User: [%s], Rate: [%s], Text: [%s], Date: [%s]" % (self.author.username,
                                                                   self.rate,
                                                                   self.text[:30],
                                                                   self.date)


class Like(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "User: [%s], Post: [%s]" % (self.user.username, self.post.text[:20])


class CommentLike(models.Model):
    user = models.ForeignKey(User)
    comment = models.ForeignKey(Comment)
    statement = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "User: [%s], Comment: [%s], Date: [%s]" % (self.user.username,
                                                          self.comment.text[:20],
                                                          self.date)
