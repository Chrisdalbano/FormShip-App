from django.core.mail import send_mail
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging
from ..utils.generate_prefixed_uuid import generate_prefixed_uuid

from ..models.user import Account, AccountMembership, User
from ..serializers.account_serializer import (
    AccountSerializer,
    AccountMembershipSerializer,
    TransferOwnershipSerializer,
)
from ..serializers.user_serializer import UserSerializer



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_account(request):
    """
    Allows authenticated users to create an account.
    """
    user = request.user
    serializer = AccountSerializer(data=request.data)
    if serializer.is_valid():
        account = serializer.save(owner=user)
        AccountMembership.objects.create(account=account, user=user, role="owner")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def transfer_ownership(request, account_id):
    """
    Allows the owner of an account to transfer ownership to another user.
    """
    account = get_object_or_404(Account, id=account_id, owner=request.user)
    serializer = TransferOwnershipSerializer(data=request.data)
    if serializer.is_valid():
        new_owner_email = serializer.validated_data["new_owner_email"]
        new_owner = get_object_or_404(User, email=new_owner_email)
        account.transfer_ownership(new_owner)
        return Response(
            {"message": "Ownership transferred successfully"},
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_account_members(request, account_id):
    """
    Lists all members of a specified account.
    """
    account = get_object_or_404(Account, id=account_id)

    if request.user not in account.members.all() and account.owner != request.user:
        return Response(
            {"error": "You do not have permission to view this account."},
            status=status.HTTP_403_FORBIDDEN,
        )

    memberships = AccountMembership.objects.filter(account=account)
    serializer = AccountMembershipSerializer(memberships, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_member(request, account_id):
    """
    Invites a new member to the account via email.
    """
    account = get_object_or_404(Account, id=account_id)

    email = request.data.get("email")
    role = request.data.get("role", "member")

    if not email:
        return Response(
            {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    user, created = User.objects.get_or_create(email=email)

    if created:
        user.set_unusable_password()  # Set a temporary unusable password until user sets it
        user.save()

    membership, created = AccountMembership.objects.get_or_create(
        account=account, user=user, defaults={"role": role}
    )

    if not created:
        return Response(
            {"error": "User is already a member of this account."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Send invitation email
    send_mail(
        subject="You've been invited to Inteqra",
        message=f"Hello,\n\nYou've been invited to join the account '{account.name}'.",
        from_email="no-reply@inteqra.com",
        recipient_list=[email],
        fail_silently=False,
    )

    serializer = AccountMembershipSerializer(membership)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_account(request, account_id):
    """
    Retrieves details about a specific account.
    """
    account = get_object_or_404(Account, id=account_id)

    if request.user not in account.members.all() and account.owner != request.user:
        return Response(
            {"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )

    serializer = AccountSerializer(account)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def set_password(request):
    """
    Allows users to set or reset their password.
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = get_object_or_404(User, email=email)
    user.set_password(password)
    user.save()

    return Response(
        {"message": "Password set successfully."}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_user(request, account_id):
    account = get_object_or_404(Account, id=account_id)

    # Permission check
    if (
        request.user != account.owner
        and not AccountMembership.objects.filter(
            account=account, user=request.user, role="admin"
        ).exists()
    ):
        return Response(
            {"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )

    email = request.data.get("email")
    role = request.data.get("role", "member")
    password = request.data.get("password")
    send_invitation = request.data.get("send_invitation", False)

    if not email or not password:
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Ensure unique ID assignment
    try:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "id": generate_prefixed_uuid("u"),  # Generate a unique ID
                "password": password,
            },
        )
    except IntegrityError as e:
        return Response(
            {"error": f"Database error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if created:
        user.set_password(password)  # Ensure the password is hashed
        user.save()

    membership, created = AccountMembership.objects.get_or_create(
        account=account, user=user, defaults={"role": role}
    )

    if not created:
        return Response(
            {"error": "User is already a member of this account."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if send_invitation:
        send_mail(
            "Account Invitation",
            f"You've been added to the account {account.name}.",
            "no-reply@inteqra.com",
            [email],
            fail_silently=False,
        )

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


logger = logging.getLogger(__name__)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_user(request, account_id, user_id):
    """
    Updates or removes a user in the account.
    """
    logger.info(
        f"Managing user: {user_id} in account: {account_id} by user: {request.user.id}"
    )

    account = get_object_or_404(Account, id=account_id)

    # Validate the user is part of the account
    membership = AccountMembership.objects.filter(
        account=account, user_id=user_id
    ).first()
    if not membership:
        return Response(
            {"error": f"User with ID {user_id} is not part of account {account_id}."},
            status=status.HTTP_404_NOT_FOUND,
        )

    user = membership.user

    # Check permissions
    if (
        request.user != account.owner
        and not AccountMembership.objects.filter(
            account=account, user=request.user, role="admin"
        ).exists()
    ):
        return Response(
            {"error": "Permission denied. Only owners or admins can modify users."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "PATCH":
        # Update user role or attributes
        role = request.data.get("role")
        user_name = request.data.get("user_name")
        user_email = request.data.get("user_email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        if role:
            membership.role = role
            membership.save()

        if user_name:
            user.username = user_name  # Update the username field
            user.save()

        if user_email:
            user.email = user_email  # Update the email field
            user.save()

        if first_name:
            user.first_name = first_name
            user.save()

        if last_name:
            user.last_name = last_name
            user.save()

        return Response(
            {"message": "User updated successfully."}, status=status.HTTP_200_OK
        )

    if request.method == "DELETE":
        # Remove the user from the account
        membership.delete()
        return Response(
            {"message": "User removed successfully."}, status=status.HTTP_200_OK
        )
