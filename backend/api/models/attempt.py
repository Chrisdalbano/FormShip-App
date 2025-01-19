import uuid
from django.db import models
from .quiz import Quiz
from .participant import Participant


class Attempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    participant = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attempts",
    )
    score = models.FloatField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    needs_manual_grading = models.BooleanField(default=False)

    def __str__(self):
        participant_name = self.participant.name if self.participant else "Anonymous"
        return f"Attempt for {self.quiz.title} by {participant_name}"
