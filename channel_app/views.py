from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User

from channel_app.models import Message, ChatRoom


# Create your views here.

def chat_index(request):
    users = [user for user in User.objects.all() if not user == request.user]
    other_users = [user for user in users if user != request.user]
    chatrooms = ChatRoom.objects.all()
    user_rooms = [room for room in chatrooms if room.is_member(request.user)]
    messages = Message.objects.all().order_by('chatroom', '-created').distinct('chatroom_id')
    sorted_messages = sorted(list(messages.values_list('id', flat=True)), reverse=True)
    user_rooms = generate_user_index_rooms(request, sorted_messages)
    return render(request, 'channel_app/chat_index2.html', {'user_rooms': user_rooms,
                                                            'other_users': other_users,
                                                            'users': users})


def generate_user_index_rooms(request, sorted_messages):
    chatroom_list = []
    chatrooms = ChatRoom.objects.all()
    chatroom_names = [room.name for room in chatrooms if room.is_member(request.user)]
    user_group_chats = [room for room in chatrooms if room.type == 'Group Chat' and room.is_member(request.user)]
    msg = Message.objects.filter(id__in=sorted_messages).filter(chatroom__name__in=chatroom_names).order_by('-id')
    for message in msg:
        chatroom_list.append(message.chatroom)

    for group in user_group_chats:
        if group.messages.count() == 0:
            chatroom_list.append(group)
    print('admin: ', )
    return chatroom_list


def create_groupchat(request):
    name = request.POST.get('room_name')
    uid_list = request.POST.getlist('users')
    users = [User.objects.get(id=uid) for uid in uid_list]
    chatroom = ChatRoom.objects.create(name=name, type="Group Chat")
    chatroom.add_member(users)
    return HttpResponseRedirect('chat_index')


def chatroom(request):
    print(request.POST)
    room_name = request.POST.get('room_name')
    if not room_name:
        user1 = request.POST.get('user1')
        user2 = request.POST.get('user2')
        uid_list = [user1, user2]
        users = [User.objects.get(id=uid) for uid in uid_list]
        room_name = '_'.join(sorted([user.username for user in users]))
        chatroom, created = ChatRoom.objects.get_or_create(name=room_name)
        if created:
            chatroom.type = 'Conversation'
            chatroom.add_member(users)
            chatroom.save()
    else:
        chatroom = ChatRoom.objects.get(name=room_name)
    users = User.objects.all()
    other_users = [user for user in users if not chatroom.is_member(user)]
    counter = 10
    messages = chatroom.messages.all().order_by('-created')
    total_count = messages.count()
    sliced = messages[:counter][::-1]
    room_members = chatroom.member.all()
    return render(request, 'channel_app/chatroom2.html', {'room_name': room_name,
                                                          'chatroom': chatroom,
                                                          'messages': sliced,
                                                          'other_users': other_users,
                                                          'counter': counter,
                                                          'total_count': total_count,
                                                          'room_members': room_members})
