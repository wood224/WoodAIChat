from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from chat.models import ChatSession, ChatMessage, ChatModel


class ChatSessionSerializer(ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ChatSession
        fields = "__all__"


class ChatModelSerializer(ModelSerializer):

    class Meta:
        model = ChatModel
        fields = "__all__"


class ChatMessageSerializer(ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ChatMessage
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["session"] = ChatSessionSerializer(instance.session).data
        data["model"] = ChatModelSerializer(instance.model).data
        return data
