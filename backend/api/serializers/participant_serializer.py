from rest_framework import serializers
from ..models.participant import Participant, QuizParticipation


class QuizParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizParticipation
        fields = ['id', 'quiz', 'final_score', 'has_completed', 'responded_at', 'created_at']
        read_only_fields = ['id', 'created_at']


class ParticipantSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    quiz_participations = QuizParticipationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Participant
        fields = ['id', 'name', 'email', 'password', 'quiz_participations', 'created_at', 'is_authenticated_user']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True}
        }
