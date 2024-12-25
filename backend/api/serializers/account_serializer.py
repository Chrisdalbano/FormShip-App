from rest_framework import serializers
from ..models.user import Account, AccountMembership, User


class AccountSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Account
        fields = ["id", "name", "owner_email", "created_at"]


class AccountMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = AccountMembership
        fields = [
            "id",
            "user_email",
            "user_name",
            "role",
            "invited_at",
            "joined_at",
            "last_connected",
        ]


class TransferOwnershipSerializer(serializers.Serializer):
    new_owner_email = serializers.EmailField()
