import os.path

from rest_framework import serializers
from channel_app.models import Message, Image
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id", "conversation", "sender", "receiver", "content", "created", "is_read"
        ]

    def get_conversation(self, obj):
        return str(obj.conversation.id)

    def get_sender(self, obj):
        return UserSerializer(obj.sender).data

    def get_receiver(self, obj):
        return UserSerializer(obj.receiver).data


class ImageUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['image']

    def validate_image(self, value):
        im = os.path.splitext(value)
        print(im)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'id']
