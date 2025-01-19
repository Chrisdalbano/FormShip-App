import uuid
from django.db import models
from .quiz import Quiz


class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="participants"
    )
    email = models.EmailField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    is_authenticated_user = models.BooleanField(default=False)
    external_identifier = models.CharField(max_length=255, null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    has_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Participant ({self.name or self.email or self.external_identifier})"
