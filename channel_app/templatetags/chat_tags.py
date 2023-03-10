from django import template
from django.db.models import Q
from django.templatetags.static import static
from datetime import datetime
from channel_app.models import ChatRoom, Message
from django.utils.timezone import utc
from datetime import datetime
register = template.Library()


@register.simple_tag()
def chatroom_last_message_time(cid):
    chatroom = ChatRoom.objects.get(id=cid)
    last_message = chatroom.messages.last()
    if last_message:
        now = datetime.utcnow().replace(tzinfo=utc)
        if last_message.created.date() == now.date():
            diff = now - last_message.created
            seconds = diff.total_seconds()
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes <= 60:
                return f"{minutes} Min Ago"
            else:
                return last_message.created.strftime("%I:%M %p").lower()
        else:
            return last_message.created.strftime("%I:%M %p").lower()
    else:
        return ""


@register.simple_tag()
def get_room_name(request, name):
    chatroom = ChatRoom.objects.get(name=name)
    if chatroom.type == 'Conversation':
        users = name.split("_")
        room_name = ''.join([user for user in users if request.user.username != user])
    elif chatroom.type == 'Group Chat':
        if '_' in chatroom.name:
            room_name = chatroom.name.replace('_', " ")
        else:
            room_name = chatroom.name
    return room_name.title()


@register.simple_tag()
def get_room_image(name):
    chatroom = ChatRoom.objects.get(name=name)
    if chatroom.type == 'Group Chat':
        img = static('img/group_chat.png')
    else:
        img = static('img/avatar1.png')
    return img


@register.simple_tag()
def chatroom_last_message(cid):
    chatroom = ChatRoom.objects.get(id=cid)
    message = chatroom.messages.last()
    if message:
        return message.content
    else:
        return ""


@register.simple_tag()
def room_message_read(request_user, rid):
    room = ChatRoom.objects.get(id=rid)
    messages = room.messages.all()
    user_message = [message for message in messages if not message.sender == request_user and not message.is_read(request_user)]
    return len(user_message)

