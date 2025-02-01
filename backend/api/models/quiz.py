import uuid
from django.db import models
from .group import Group
from .user import Account
from ..utils import generate_prefixed_uuid
from django.utils.timezone import now
from .participant import Participant
from django.utils.timezone import now
from django.urls import reverse


def generate_quiz_id():
    return generate_prefixed_uuid("q")


class Quiz(models.Model):

    def get_shareable_url(self):
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        base_url = f"https://{current_site.domain}"
        
        # Different URL formats based on access control
        if self.access_control == 'login_required':
            return f"{base_url}/quiz/access/{self.id}"
        elif self.access_control == 'invitation':
            return f"{base_url}/quiz/invite/{self.id}"
        else:  # public
            return f"{base_url}/quiz/{self.id}"

    EVALUATION_CHOICES = [
        ("pre", "Pre-Evaluated"),
        ("hybrid", "Hybrid"),
        ("post", "Post-Evaluated"),
    ]

    ACCESS_CONTROL_CHOICES = [
        ("public", "Public"),  # Anyone with the link can access
        ("invitation", "Invitation"),  # Only invited users can access
        ("login_required", "Login"),  # Must be a logged-in user
        # You can add more if needed, e.g. domain-limited, etc.
    ]

    id = models.CharField(
        primary_key=True,
        max_length=50,
        default=generate_quiz_id,
        editable=False,
        unique=True,
    )

    account = models.ForeignKey(
        Account, related_name="quizzes", on_delete=models.CASCADE
    )

    account = models.ForeignKey(
        Account, related_name="quizzes", on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        Group, related_name="quizzes", on_delete=models.SET_NULL, null=True, blank=True
    )
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50, default="medium")
    question_count = models.IntegerField(default=0)
    display_results = models.BooleanField(default=True)
    require_password = models.BooleanField(default=False)
    password = models.CharField(max_length=255, null=True, blank=True)
    allow_anonymous = models.BooleanField(default=False)
    require_name = models.BooleanField(default=False)
    quiz_type = models.CharField(max_length=50, default="multiple-choice")
    created_at = models.DateTimeField(auto_now_add=True)
    quiz_time_limit = models.IntegerField(null=True, blank=True)
    are_questions_timed = models.BooleanField(default=False)
    time_per_question = models.IntegerField(null=True, blank=True)
    is_timed = models.BooleanField(default=False)
    skippable_questions = models.BooleanField(default=True)
    segment_steps = models.BooleanField(default=False)
    allow_previous_questions = models.BooleanField(default=False)
    evaluation_type = models.CharField(
        max_length=10,
        choices=[
            ("pre", "Pre-Evaluated"),
            ("hybrid", "Hybrid"),
            ("post", "Post-Evaluated"),
        ],
        default="pre",
    )
    is_testing = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    access_control = models.CharField(
        max_length=20,
        choices=ACCESS_CONTROL_CHOICES,
        default="public",
        help_text="Determines who can access the quiz.",
    )
    allow_review = models.BooleanField(
        default=True,
        help_text="Allow participants to review their answers after completion"
    )
    review_window = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Number of days participants can review their answers (null for unlimited)"
    )

    def __str__(self):
        return self.title


class SharedQuiz(models.Model):
    id = models.CharField(
        max_length=36,  #
        primary_key=True,
        default=generate_prefixed_uuid("sh"),
        editable=False,
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="shared_quizzes"
    )
    share_link = models.URLField()
    requires_authentication = models.BooleanField(default=False)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shared Quiz: {self.quiz.title}"


class QuizEventLog(models.Model):
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, related_name="events")
    participant_id = models.CharField(
        max_length=255, null=True, blank=True
    )  # Anonymous or logged-in user
    event_type = models.CharField(max_length=100)  # e.g., 'NEXT_QUESTION', 'SUBMIT'
    details = models.JSONField(default=dict)  # Flexible structure for event metadata
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.event_type} - {self.quiz.title} at {self.timestamp}"


class QuizSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="submissions")
    participant = models.ForeignKey(
        "api.Participant",  # Use string reference to avoid import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )
    answers = models.JSONField(default=dict)  # Stores submitted answers
    score = models.FloatField(null=True, blank=True)  # Final calculated score
    submitted_at = models.DateTimeField(default=now)
    is_completed = models.BooleanField(default=True)  # Flag for completion
    duration = models.IntegerField(null=True, blank=True)  # Time taken in seconds

    def __str__(self):
        participant_name = self.participant.name if self.participant else "Anonymous"
        return f"Submission for {self.quiz.title} by {participant_name}"
