from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import utc
import uuid

User = get_user_model()
""""
Chatroom :type
Conversation
Group Chat
"""


class Image(models.Model):
    image = models.ImageField(upload_to='chat_images')


class ChatRoom(models.Model):
    CHATROOM_CHOICES = (
        ('Conversation', 'Conversation'),
        ('Group Chat', 'Group Chat'),
    )
    name = models.CharField(max_length=128, unique=True)
    online = models.ManyToManyField(to=User, blank=True)
    type = models.CharField(max_length=128, choices=CHATROOM_CHOICES, default="Conversation")
    member = models.ManyToManyField(User, related_name='members', blank=True)

    def is_member(self, user):
        """
        check if the user is a member of a chatroom
        :param user:
        :return:
        """
        return user in self.member.all()

    def add_member(self, users):
        """
        add a user to a chatroom
        :param users:
        :return:
        """
        self.member.add(*users)
        self.save()

    def remove_members(self, users):
        """
        remove a user from a chatroom
        :param users:
        :return:
        """
        self.member.remove(*users)
        self.save()

    def get_online_count(self):
        """
        return the count of all online member of a chatroom
        :return:
        """
        return self.online.count()

    def join(self, user):
        """
        add user to the online member of a chatroom
        :param user:
        :return:
        """
        self.online.add(user)
        self.save()

    def leave(self, user):
        """
        remove user from the online member of a chatroom
        :param user:
        :return:
        """
        self.online.remove(user)
        self.save()

    def read_all_unread(self, user):
        """
        will add the user to the members that read the chat
        :param user:
        :return:
        """
        messages = [message for message in self.messages.all() if not message.sender == user and not message.is_read(user)]
        for message in messages:
            message.read(user)

    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name.replace(" ", "_")
        return super(ChatRoom, self).save()


class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver', blank=True, null=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    # is_read = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, blank=True)

    def __str__(self):
        receiver = self.receiver if self.receiver else None
        return f"from {self.sender.username} to {receiver}"

    def is_read(self, user):
        return user in self.read_by.all()

    def read(self, user):
        self.read_by.add(user)
        self.save()


class Notifications(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, related_name='notifications')
    message = models.TextField()
