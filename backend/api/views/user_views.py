from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from ..serializers.user_serializer import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.timezone import now
from ..models.user import User, AccountMembership, Account, UserResult
from ..serializers.user_serializer import (
    UserSerializer,
    RegisterSerializer,
    UserResultSerializer,
)
from ..serializers.account_serializer import AccountMembershipSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = self.serializer_class().get_user()
            user.last_connected = now()
            user.save()
        return response


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Allows an authenticated user to change their password.
    """
    user = request.user
    current_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    confirm_new_password = request.data.get("confirm_new_password")

    if not check_password(current_password, user.password):
        return Response(
            {"error": "Current password is incorrect."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_password != confirm_new_password:
        return Response(
            {"error": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save()

    return Response(
        {"message": "Password updated successfully."}, status=status.HTTP_200_OK
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Retrieves or updates the authenticated user's profile.
    """
    user = request.user

    if request.method == "GET":
        serializer = RegisterSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = RegisterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_user(request, account_id):
    """
    Allows the account owner to invite a user to join their account.
    """
    account = get_object_or_404(Account, id=account_id, owner=request.user)
    email = request.data.get("email")
    role = request.data.get("role", "member")

    if not email:
        return Response(
            {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    user, created = User.objects.get_or_create(email=email)

    if created:
        user.set_unusable_password()  # Temporary password until they set a new one
        user.save()

    membership, created = AccountMembership.objects.get_or_create(
        account=account, user=user, defaults={"role": role}
    )

    if not created:
        return Response(
            {"error": "User is already a member of this account."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Send invitation email with instructions to set a password
    send_mail(
        subject="You're invited to join Inteqra",
        message=(
            f"Hello,\n\nYou've been invited to join the account '{account.name}'. "
            "Please set your password to activate your account.\n\n"
            "Visit: <password_reset_link>"
        ),
        from_email="no-reply@inteqra.com",
        recipient_list=[email],
        fail_silently=False,
    )

    return Response(
        {"message": "Invitation sent successfully."}, status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
def register_user(request):
    """
    Allows registration of a new user.
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def set_password(request):
    """
    Allows a user to set or reset their password.
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
def submit_quiz_results(request):
    """
    Submit results for a quiz.
    """
    quiz_id = request.data.get("quiz_id")
    score = request.data.get("score")
    user = request.user

    if not quiz_id or score is None:
        return Response(
            {"error": "Quiz ID and score are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    quiz = get_object_or_404(UserResult, id=quiz_id)
    serializer = UserResultSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user, quiz=quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_account_members(request, account_id):
    """
    List all members of an account, including their roles.
    """
    account = get_object_or_404(Account, id=account_id)

    if request.user not in account.members.all() and account.owner != request.user:
        return Response(
            {"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )

    memberships = AccountMembership.objects.filter(account=account)
    serializer = AccountMembershipSerializer(memberships, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_user(request, account_id):
    """
    Allows account owners to create a new user directly under their account.
    """
    account = get_object_or_404(Account, id=account_id, owner=request.user)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        AccountMembership.objects.create(account=account, user=user, role="member")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_quiz_result(request, result_id):
    """
    Retrieve quiz results for a specific user.
    """
    result = get_object_or_404(UserResult, id=result_id)
    serializer = UserResultSerializer(result)
    return Response(serializer.data, status=status.HTTP_200_OK)
