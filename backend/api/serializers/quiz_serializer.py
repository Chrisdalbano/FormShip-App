from rest_framework import serializers
from ..models.quiz import Quiz, SharedQuiz, QuizSubmission
from ..models.quiz_invite import InvitedUser

# from ..models.question import Question
from .question_serializer import QuestionSerializer


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    shareable_url = serializers.SerializerMethodField()  # Add this field

    class Meta:
        model = Quiz
        fields = [
            "id",
            "account",
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
            "are_questions_timed",
            "time_per_question",
            "is_timed",
            "questions",
            "skippable_questions",
            "segment_steps",
            "allow_previous_questions",
            "evaluation_type",
            "is_testing",
            "is_published",
            "access_control",
            "questions",
            "shareable_url",  # Include in the serializer
        ]

    def get_shareable_url(self, obj):
        """Generate a shareable URL for the quiz."""
        request = self.context.get("request")
        if obj.is_published and request:
            return request.build_absolute_uri(f"/quiz/{obj.id}/")
        return None

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


class InvitedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitedUser
        fields = ["id", "quiz", "email", "invited_at", "has_responded"]
        read_only_fields = ["invited_at", "has_responded"]


class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = [
            'id', 
            'quiz', 
            'participant', 
            'participation',
            'answers', 
            'score', 
            'duration', 
            'is_completed', 
            'submitted_at'
        ]
        read_only_fields = ['id', 'submitted_at']
