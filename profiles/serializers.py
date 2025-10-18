from rest_framework import serializers
from .models import Profile,Messages

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name', 'bio', 'phone', 'address', 'profile_image']
        depth = 1
        read_only_fields = ['user']

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    receiver_username = serializers.CharField(source="receiver.username", read_only=True)

    class Meta:
        model = Messages
        fields = ['id', 'sender', 'sender_username', 'receiver', 'receiver_username', 'subject', 'content','status','created_at']
        read_only_fields = ['sender', 'created_at']