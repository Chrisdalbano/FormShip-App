from django.db import models
from .group import Group
from .user import Account


class Quiz(models.Model):
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

    account = models.ForeignKey(
        Account, related_name="quizzes", on_delete=models.CASCADE
    )  # Link quiz to account
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
    quiz_time_limit = models.IntegerField(null=True, blank=True)  # in minutes
    are_questions_timed = models.BooleanField(default=False)  # New field
    time_per_question = models.IntegerField(null=True, blank=True)  # in seconds
    is_timed = models.BooleanField(default=False)
    skippable_questions = models.BooleanField(default=True)
    segment_steps = models.BooleanField(default=False)
    allow_previous_questions = models.BooleanField(default=False)  # New field

    evaluation_type = models.CharField(
        max_length=10,
        choices=EVALUATION_CHOICES,
        default="pre",
        help_text="Determines if the quiz is pre-evaluated, hybrid, or post-evaluated.",
    )
    is_testing = models.BooleanField(
        default=False,
        help_text="If True, quiz attempts won't be officially recorded in analytics/results.",
    )
    is_published = models.BooleanField(
        default=False,
        help_text="Indicates if the quiz is published (visible to participants).",
    )
    access_control = models.CharField(
        max_length=20,
        choices=ACCESS_CONTROL_CHOICES,
        default="public",
        help_text="Determines who can access the quiz.",
    )

    def __str__(self):
        return self.title


class SharedQuiz(models.Model):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="shared_quizzes"
    )
    share_link = models.URLField()
    requires_authentication = models.BooleanField(default=False)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shared Quiz: {self.quiz.title}"
