from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models.user import UserResult
from ..models.quiz import Quiz
from ..serializers.user_serializer import UserResultSerializer
from django.shortcuts import get_object_or_404


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
