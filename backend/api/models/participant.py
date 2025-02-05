import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Participant(models.Model):
    """
    Represents a participant who can take multiple quizzes.
    Quiz-specific data is stored in QuizParticipation model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_authenticated_user = models.BooleanField(default=False)
    external_identifier = models.CharField(max_length=255, null=True, blank=True)

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


class QuizParticipation(models.Model):
    """
    Represents a participant's involvement in a specific quiz.
    Stores quiz-specific data like scores and completion status.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='quiz_participations')
    quiz = models.ForeignKey('api.Quiz', on_delete=models.CASCADE, related_name='participations')
    final_score = models.FloatField(null=True, blank=True)
    has_completed = models.BooleanField(default=False)
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participant', 'quiz')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.participant.name} - {self.quiz.title}"
