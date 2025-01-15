from rest_framework import serializers
from ..models.group import Group
from .quiz_serializer import QuizSerializer


class GroupSerializer(serializers.ModelSerializer):
    quizzes = QuizSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ["id", "name", "account", "color", "order", "created_at", "quizzes"]
