# backend/api/serializers.py

from rest_framework import serializers
from .models import Quiz, Question, UserQuizHistory, SharedQuiz, UserResult


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
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
            "created_at",
        ]


class UserQuizHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuizHistory
        fields = "__all__"


class SharedQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedQuiz
        fields = "__all__"

class UserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResult
        fields = ['quiz', 'user_name', 'score', 'total_questions', 'created_at']