from django.contrib import admin

from users.models import UserProfile, UserNotification, UserRate, UserReport, UserFeed, UserRequest, UserInfinityBan

admin.site.register(UserProfile)
admin.site.register(UserNotification)
admin.site.register(UserRate)
admin.site.register(UserReport)
admin.site.register(UserFeed)
admin.site.register(UserRequest)
admin.site.register(UserInfinityBan)
