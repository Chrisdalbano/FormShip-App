# backend/api/serializers/user_serializer.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from ..models.user import UserQuizHistory, UserResult, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "company",
            "organization_type",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            company=validated_data.get("company"),
            organization_type=validated_data.get("organization_type"),
        )
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["email"] = user.email
        return token


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
