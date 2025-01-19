from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ..models.user import UserQuizHistory, UserResult, Account, AccountMembership

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    account_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "company",
            "organization_type",
            "account_id",
        ]

    def get_account_id(self, user):
        owner_account = Account.objects.filter(owner=user).first()
        if owner_account:
            return owner_account.id
        membership = AccountMembership.objects.filter(user=user).first()
        if membership:
            return membership.account.id
        return None

    def validate_password(self, value):
        if len(value) < 4:
            raise serializers.ValidationError(
                "Password must be at least 4 characters long."
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must include at least one numeric character."
            )
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError(
                "Password must include at least one letter."
            )
        return value

    def create(self, validated_data):
        if User.objects.filter(email=validated_data["email"]).exists():
            raise ValidationError("A user with this email already exists.")
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            company=validated_data.get("company"),
            organization_type=validated_data.get("organization_type"),
        )
        account = Account.objects.create(
            name=f"{user.first_name or 'User'}'s Account", owner=user
        )
        user.save()
        AccountMembership.objects.create(account=account, user=user, role="owner")
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
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


class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "company",
            "organization_type",
        ]
