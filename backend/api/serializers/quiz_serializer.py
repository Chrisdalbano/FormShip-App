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
            "are_questions_timed",  # New field
            "time_per_question",
            "is_timed",
            "questions",
            "skippable_questions",
            "segment_steps",
            "allow_previous_questions",
        ]

    def validate(self, data):
        if data.get("require_password") and not data.get("password"):
            raise serializers.ValidationError(
                "Password is required if 'require_password' is True."
            )
        if data.get("are_questions_timed") and not data.get("time_per_question"):
            raise serializers.ValidationError(
                "Time per question is required if 'are_questions_timed' is True."
            )
        return data


class SharedQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedQuiz
        fields = ["id", "quiz", "share_link", "requires_authentication", "shared_at"]
