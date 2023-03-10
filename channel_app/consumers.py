from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from channel_app.api.serializers import MessageSerializer, UserSerializer
from channel_app.models import ChatRoom, Message


class ChatConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(ChatConsumer, self).__init__(*args, **kwargs)
        self.chatroom = None
        self.chatroom_name = None
        self.user = None

    def connect(self):
        self.chatroom_name = f"{self.scope['url_route']['kwargs']['chatroom_name']}"
        print('------------socket connected successfully----------')
        self.user = self.scope['user']
        self.accept()
        if not self.user.is_authenticated:
            self.close()
        else:
            async_to_sync(self.channel_layer.group_add)(self.chatroom_name, self.channel_name)
            self.chatroom, _ = ChatRoom.objects.get_or_create(name=self.chatroom_name)
            self.chatroom.join(self.user)
            self.chatroom.read_all_unread(self.user)

            self.send_json({
                'type': 'welcome_message',
                'message': 'good day boss, you are connected successfully'
            })
            async_to_sync(self.channel_layer.group_send)(self.chatroom_name, {
                'type': 'join_group',
                'message': f"{self.user.username} joined the {self.chatroom.type}.",
            })
            # async_to_sync(self.channel_layer.group_send)(self.chatroom_name, {
            #     'type': 'read_message',
            #     'message'
            # })

    def disconnect(self, code):
        print('--------- Disconnecting -------------')
        if self.user.is_authenticated:
            self.chatroom.leave(self.user)
            self.send_json({
                'type': 'user_leave',
                'message': 'You disconnect from the websocket successfully.'
            })
        return super(ChatConsumer, self).disconnect(code)

    def receive_json(self, content, **kwargs):
        message_type = content['type']
        if message_type == 'chat_message':
            message = Message.objects.create(chatroom=self.chatroom, sender=self.user,
                                             content=content['message'], receiver=self.get_receiver(self.chatroom))
            message.read(self.user)
            async_to_sync(self.channel_layer.group_send)(self.chatroom_name, {
                'type': 'chat_message',
                'message': content['message'],
                'user': self.user.username,
                'time': message.created.strftime("%I:%M %p").lower()
            })
        elif message_type == 'add_user':
            users = content['users']
            user = content['user']
            users_list = [User.objects.get(id=uid) for uid in users]
            users = ', '.join([user.username for user in users_list])
            room_member = self.chatroom.member.all()
            self.chatroom.add_member(users_list)
            other_user = [user for user in User.objects.all() if not self.chatroom.is_member(user)]
            async_to_sync(self.channel_layer.group_send)(self.chatroom_name, {
                'type': 'add_user_echo',
                'users': users,
                'message': f"{user} Added {users}",
                'other_users': UserSerializer(other_user, many=True).data,
                'room_members': UserSerializer(room_member, many=True).data
            })

        elif message_type == 'remove_user':
            users = content['users']
            user = content['user']
            users_list = [User.objects.get(id=uid) for uid in users]
            users = ', '.join([user.username for user in users_list])
            self.chatroom.remove_members(users_list)
            other_user = [user for user in User.objects.all() if not self.chatroom.is_member(user)]
            room_member = self.chatroom.member.all()
            async_to_sync(self.channel_layer.group_send)(self.chatroom_name, {
                'type': 'remove_user_echo',
                'users': users,
                'message': f"{user} Removed {users}",
                'other_users': UserSerializer(other_user, many=True).data,
                'room_members': UserSerializer(room_member, many=True).data
            })

        elif message_type == 'search_chatroom':
            keyword = content['keyword']
            print('keyword: ', keyword)
            user = content['user']
            result = self.search_room(keyword, user)
            async_to_sync(self.channel_layer.group_send)(self.chatroom_name, {
                'type': 'search_room_echo',
                'result': result,
                'searcher': self.user.username
            })

        elif message_type == 'reload_chats':
            user = content['user']
            result = self.reload_chats(user)
            async_to_sync(self.channel_layer.group_send)(self.chatroom_name, {
                'type': 'reload_chat_echo',
                'results': result,
                'user': self.user.username
            })

        elif message_type == 'scroll_load_chat':
            counter = content['counter']
            scroller = content['scroller']
            result = self.previous_chats(counter)
            async_to_sync(self.channel_layer.group_send)(self.chatroom_name, {
                'type': 'scroll_load_chat_echo',
                'result': result,
                'user': scroller
            })

        return super(ChatConsumer, self).receive_json(content, **kwargs)

    def close(self, code=None):
        self.send_json({
            'type': 'not_authenticated',
            'message': 'You are not authenticated'
        })
        return super(ChatConsumer, self).close()

    def chat_message(self, event):
        self.send_json(event)

    def join_group(self, event):
        self.send_json(event)

    def add_user_echo(self, event):
        self.send_json(event)

    def remove_user_echo(self, event):
        self.send_json(event)

    def search_room_echo(self, event):
        self.send_json(event)

    def reload_chat_echo(self, event):
        self.send_json(event)

    def scroll_load_chat_echo(self, event):
        self.send_json(event)

    def get_receiver(self, chatroom):
        if chatroom.type == 'Conversation':
            name = chatroom.name.split('_')
            receiver = ''.join([n for n in name if n != self.user.username])
            receiver = User.objects.get(username=receiver)
        else:
            receiver = None

        return receiver

    def search_room(self, keyword, user):
        messages = self.chatroom.messages.all()
        result_list = []
        for message in messages:
            if str(keyword) in message.content:
                temp = render_to_string('channel_app/chatroom_chat_box.html', {'message': message,
                                                                               'user': user,
                                                                               'time': message.created.strftime(
                                                                                   "%I:%M %p").lower()})
                result_list.append(temp)
        return ''.join(result_list)

    def reload_chats(self, user):
        messages = self.chatroom.messages.all()
        result_list = []
        for message in messages:
            temp = render_to_string('channel_app/chatroom_chat_box.html', {'message': message,
                                                                           'user': user,
                                                                           'time': message.created.strftime(
                                                                               "%I:%M %p").lower()})
            result_list.append(temp)
        out = ''.join(result_list)
        return out

    def previous_chats(self, counter):
        messages = self.chatroom.messages.all().order_by('created')[::-1][:counter][::-1]
        result_list = []
        for message in messages:
            temp = render_to_string('channel_app/chatroom_chat_box.html', {'message': message,
                                                                           'time': message.created.strftime(
                                                                               "%I:%M %p").lower()})
            result_list.append(temp)
        out = ''.join(result_list)
        return out


