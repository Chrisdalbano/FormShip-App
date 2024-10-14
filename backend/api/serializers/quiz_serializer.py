from rest_framework import serializers
from ..models.quiz import Quiz, SharedQuiz
from ..models.question import Question
from .question_serializer import QuestionSerializer


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "group",
            "order",
            "title",
            "topic",
            "difficulty",
            "question_count",
            "display_results",
            "require_password",
            "password",
            "allow_anonymous",
            "require_name",
            "quiz_type",
            "created_at",
            "quiz_time_limit",
            "time_per_question",
            "is_timed",
            "question_time_limit",
            "questions",
        ]


class SharedQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedQuiz
        fields = ["id", "quiz", "share_link", "requires_authentication", "shared_at"]
