# backend/api/serializers.py

from rest_framework import serializers
from .models import Quiz, Question, UserQuizHistory, SharedQuiz, UserResult, Group


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = [
            "id",
            "group",
            "title",
            "topic",
            "difficulty",
            "question_count",
            "display_results",
            "require_password",
            "password",
            "allow_anonymous",
            "require_name",
            "created_at",
        ]


class GroupSerializer(serializers.ModelSerializer):
    quizzes = QuizSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'color', 'order', 'created_at', 'quizzes']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "option_e",
            "correct_answer",
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(
        many=True, read_only=True
    )  # Nesting QuestionSerializer

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "topic",
            "difficulty",
            "question_count",
            "quiz_type",
            "questions",
            "allow_anonymous",
            "require_password",
            "password",
            "require_name",
            "display_results",
        ]

    def validate_questions(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("A quiz must have at least 1 question.")
        if len(value) > 25:
            raise serializers.ValidationError("A quiz can have up to 25 questions.")
        return value


class UserQuizHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuizHistory
        fields = "__all__"


class SharedQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedQuiz
        fields = [
            "id",
            "quiz",
            "share_link",
            "requires_authentication",
            "shared_at",
        ]


class UserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResult
        fields = [
            "quiz",
            "user_name",
            "score",
            "total_questions",
            "completed_at",
            "anonymous_id",
        ]
