from rest_framework import serializers
from .models import Event, Registration, Ticket, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date_time', 'location']

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['id', 'event', 'user', 'registration_date', 'ticket_type', 'number_of_tickets']
