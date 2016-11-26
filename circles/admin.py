from django.contrib import admin

from circles.models import Circle, UserCircle, Topic, Group, TopicComment

admin.site.register(Circle)
admin.site.register(UserCircle)
admin.site.register(Topic)
admin.site.register(Group)
admin.site.register(TopicComment)
