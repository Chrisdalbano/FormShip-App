# backend/api/serializers/user_serializer.py

from rest_framework import serializers
from ..models.user import UserQuizHistory, UserResult


class UserQuizHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuizHistory
        fields = ["id", "user", "quiz", "score", "xp_earned", "timestamp"]


class UserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResult
        fields = [
            "id",
            "quiz",
            "user",
            "nickname",
            "score",
            "completed_at",
            "anonymous_id",
        ]
