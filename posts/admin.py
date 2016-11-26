from django.contrib import admin

from posts.models import Post, PostHashtag, Comment, Like, CommentLike

admin.site.register(Post)
admin.site.register(PostHashtag)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(CommentLike)
