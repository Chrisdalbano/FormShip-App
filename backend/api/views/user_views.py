from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from ..models.user import UserResult
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password


from ..models.quiz import Quiz
from ..serializers.user_serializer import (
    MyTokenObtainPairSerializer,
    UserResultSerializer,
    RegisterSerializer,
)
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    confirm_new_password = request.data.get("confirm_new_password")

    # Check if the current password matches
    if not check_password(current_password, user.password):
        return Response(
            {"error": "Current password is incorrect."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if the new password and confirmation match
    if new_password != confirm_new_password:
        return Response(
            {"error": "New passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update the password
    user.set_password(new_password)
    user.save()

    return Response(
        {"message": "Password updated successfully."},
        status=status.HTTP_200_OK
    )

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user

    if request.method == "GET":
        serializer = RegisterSerializer(user)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = RegisterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["POST"])
def submit_quiz_results(request):
    quiz_id = request.data.get("quiz_id")
    quiz = get_object_or_404(Quiz, id=quiz_id)

    serializer = UserResultSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(quiz=quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_quiz_result(request, result_id):
    result = get_object_or_404(UserResult, id=result_id)
    serializer = UserResultSerializer(result)
    return Response(serializer.data)
