# api/models/quiz_event.py
from django.db import models
from django.utils import timezone
from .quiz import Quiz


class QuizEvent(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    # Possibly store participant_email or an ephemeral ID
    participant_email = models.EmailField(null=True, blank=True)
    event_type = models.CharField(max_length=50)
    event_detail = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Event {self.event_type} at {self.timestamp} for quiz {self.quiz_id}"
