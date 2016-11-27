from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import *

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'location', 'is_staff']

    def location(self, obj):
    	if obj.is_staff:
    		return ''
        return "({}, {})".format(obj.info.latitude, obj.info.longitude)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(UserProfile)
admin.site.register(UserNotification)
admin.site.register(UserRate)
admin.site.register(UserReport)
admin.site.register(UserFeed)
admin.site.register(UserRequest)
admin.site.register(UserInfinityBan)
