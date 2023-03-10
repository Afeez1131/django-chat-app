from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.template.loader import render_to_string

from channel_app.models import ChatRoom, Message
from channel_app.views import generate_user_index_rooms


def ajax_create_group_chat(request):
    print(request.POST)
    users = request.POST.getlist('users[]')
    name = request.POST.get('room_name')
    try:
        chatroom = ChatRoom.objects.create(name=name)
        chatroom.type = 'Group Chat'
        chatroom.add_member(users)
        chatroom.add_member([request.user.id])
        chatroom.save()
        temp = render_to_string('channel_app/index_user_list.html', {'room': chatroom,
                                                                     'request': request})
        return JsonResponse({'response': 'success', 'out': ''.join(temp)})
    except IntegrityError:
        return JsonResponse({'integrity_error': 'Group Chat with this name exist'})


def validate_room_name(request):
    name = request.POST.get('room_name')
    if ChatRoom.objects.filter(name=name).exists():
        return JsonResponse({'exist': True})
    else:
        return JsonResponse({'exist': False})


def ajax_search_index(request):
    keyword = request.POST.get('keyword')
    messages = Message.objects.all().order_by('chatroom', '-created').distinct('chatroom_id')
    sorted_messages = sorted(list(messages.values_list('id', flat=True)), reverse=True)
    user_rooms = generate_user_index_rooms(request, sorted_messages)
    result_list = []
    for room in user_rooms:
        if keyword in room.name.lower():
            temp = render_to_string('channel_app/index_user_list.html', {'room': room,
                                                                         'request': request})
            result_list.append(temp)

    return JsonResponse({'response': ''.join(result_list)})


def reload_index_room(request):
    out = []
    messages = Message.objects.all().order_by('chatroom', '-created').distinct('chatroom_id')
    sorted_messages = sorted(list(messages.values_list('id', flat=True)), reverse=True)
    user_rooms = generate_user_index_rooms(request, sorted_messages)
    for room in user_rooms:
        temp = render_to_string('channel_app/index_user_list.html', {'room': room,
                                                                     'request': request})
        out.append(temp)
    return JsonResponse({'response': ''.join(out)})
