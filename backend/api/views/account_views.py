from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        message=(
            f"Hello,\n\nYou've been invited to join the account '{account.name}'."
        ),
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
    password = request.data.get("password")
    role = request.data.get("role", "member")
    send_invitation = request.data.get("send_invitation", False)

    if not email or not password:
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user, created = User.objects.get_or_create(email=email)
    if created:
        user.set_password(password)
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
            f"You've been added to the account '{account.name}'.",
            "no-reply@inteqra.com",
            [email],
            fail_silently=False,
        )

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
