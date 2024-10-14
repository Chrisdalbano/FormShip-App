from django.db import models
from django.contrib.auth.models import User
from .quiz import Quiz


class UserQuizHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    xp_earned = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History of {self.user.username} for quiz {self.quiz.title}"


class UserResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    anonymous_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        user_name = self.user.username if self.user else self.nickname or "Anonymous"
        return f"Result for {user_name} in quiz {self.quiz.title}"
