from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from ..models.user import UserResult
from rest_framework.permissions import IsAuthenticated

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
