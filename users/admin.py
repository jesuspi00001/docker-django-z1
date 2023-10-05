from django.contrib import admin
from .models import User, Idea, FollowRequest, UserFollowerList, Notification

# Register your models here.
admin.site.register(User)
admin.site.register(Idea)
admin.site.register(FollowRequest)
admin.site.register(UserFollowerList)
admin.site.register(Notification)