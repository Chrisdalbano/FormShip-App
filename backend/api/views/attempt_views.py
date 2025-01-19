from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models.quiz import Quiz
from ..models.attempt import Attempt
from ..serializers.attempt_serializer import AttemptSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_attempts(request, quiz_id):
    """
    Fetch all attempts for a specific quiz.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = Attempt.objects.filter(quiz=quiz)
    serializer = AttemptSerializer(attempts, many=True)
    return Response(serializer.data, status=200)
