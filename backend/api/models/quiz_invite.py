# api/models/quiz_invite.py
from django.db import models
from .quiz import Quiz


class InvitedUser(models.Model):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="invited_users"
    )
    email = models.EmailField()
    invited_at = models.DateTimeField(auto_now_add=True)
    has_responded = models.BooleanField(default=False)
    # Optionally track if they have started or completed the quiz, etc.

    def __str__(self):
        return f"Invite to {self.quiz.title} for {self.email}"
