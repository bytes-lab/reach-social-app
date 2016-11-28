from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import *

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'location', 'is_staff']
    search_fields = ['username', 'email', 'info__city_name', 
    	'info__state_name', 'info__country_name']

    def location(self, obj):
    	if obj.is_staff:
    		return ''
        return "({}, {}, {})".format(obj.info.city_name, obj.info.state_name, 
        	obj.info.country_name)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(UserProfile)
admin.site.register(UserNotification)
admin.site.register(UserRate)
admin.site.register(UserReport)
admin.site.register(UserFeed)
admin.site.register(UserRequest)
admin.site.register(UserInfinityBan)
