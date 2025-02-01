from rest_framework import serializers
from ..models.participant import Participant
from django.contrib.auth.hashers import make_password


class ParticipantSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Participant
        fields = ['id', 'quiz', 'name', 'email', 'password', 'final_score', 'created_at', 'is_authenticated_user']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'quiz': {'required': False},  # Make quiz optional
            'name': {'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        """Handle password hashing on create"""
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        """Handle password hashing on update"""
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)
