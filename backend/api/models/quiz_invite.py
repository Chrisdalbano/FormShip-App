import uuid
from django.db import models
from .quiz import Quiz


class InvitedUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="invited_users"
    )
    email = models.EmailField()
    invited_at = models.DateTimeField(auto_now_add=True)
    has_responded = models.BooleanField(default=False)

    def __str__(self):
        return f"Invite to {self.quiz.title} for {self.email}"
