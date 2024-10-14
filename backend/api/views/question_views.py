from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models.question import Question
from ..models.quiz import Quiz
from ..serializers.question_serializer import QuestionSerializer


@api_view(["GET", "PUT", "DELETE"])
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == "GET":
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def create_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(quiz=quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
