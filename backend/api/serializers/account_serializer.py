from rest_framework import serializers

from ..serializers.user_serializer import UserSerializer
from ..models.user import Account, AccountMembership, User


class AccountSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Account
        # Note that ID is different from user_id thats why we pass it as another field
        # This allows control from the request on the endpoint to select the correct user_id
        # connected to an account
        fields = ["id", "name", "owner_email", "created_at"]


class AccountMembershipSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(read_only=True)
    user = UserSerializer(read_only=True)
    user_email = serializers.EmailField(source="user.email")
    user_name = serializers.CharField(source="user.get_full_name", allow_blank=True)
    user_id = serializers.CharField(
        source="user.id"
    )  # Changed from IntegerField to CharField

    class Meta:
        model = AccountMembership
        fields = [
            "user",
            "account",
            "user_id",
            "user_email",
            "user_name",
            "role",
            "invited_at",
            "joined_at",
            "last_connected",
        ]


class TransferOwnershipSerializer(serializers.Serializer):
    new_owner_email = serializers.EmailField()
