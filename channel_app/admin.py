from django.contrib import admin
from .models import ChatRoom, Message, Notifications

admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(Notifications)
