import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(
        "api.Quiz",  # Use string reference to avoid circular import
        on_delete=models.CASCADE,
        related_name="participants",
        null=True,  # Allow null for general participants
        blank=True
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255, null=True, blank=True)
    final_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_authenticated_user = models.BooleanField(default=False)
    external_identifier = models.CharField(max_length=255, null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    has_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.email})"

    def set_password(self, raw_password):
        """Set the password with proper hashing"""
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        """Check if the provided password matches"""
        if not self.password:
            return False
        return check_password(raw_password, self.password)

    class Meta:
        unique_together = ('quiz', 'email')
