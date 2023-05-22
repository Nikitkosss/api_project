from newsletter.models import Client, MailingList, Message
from rest_framework import serializers


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Message


class MailingListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MailingList
