# backend/api/models.py

from django.db import models
from django.contrib.auth.models import User
import uuid


class Group(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#FFFFFF")  # Optional color field
    order = models.PositiveIntegerField(default=0)  # Field for managing group order
    created_at = models.DateTimeField(auto_now_add=True)  # New created_at field

    def __str__(self):
        return self.name


class Quiz(models.Model):
    group = models.ForeignKey(
        Group, related_name="quizzes", on_delete=models.SET_NULL, null=True, blank=True
    )
    order = models.PositiveIntegerField(default=0)  # New order field
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50, default="medium")
    question_count = models.IntegerField(default=0)
    display_results = models.BooleanField(default=True)
    require_password = models.BooleanField(default=False)
    password = models.CharField(max_length=255, null=True, blank=True)
    allow_anonymous = models.BooleanField(default=False)
    require_name = models.BooleanField(default=False)
    quiz_type = models.CharField(
        max_length=50, default="multiple-choice"
    )  # Add back if needed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255, null=True, blank=True)
    option_d = models.CharField(max_length=255, null=True, blank=True)
    option_e = models.CharField(max_length=255, null=True, blank=True)
    correct_answer = models.CharField(max_length=1)

    def __str__(self):
        return self.question_text


class SharedQuiz(models.Model):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="shared_quizzes"
    )
    share_link = models.URLField()
    requires_authentication = models.BooleanField(default=False)
    shared_at = models.DateTimeField(auto_now_add=True)


class UserQuizHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    xp_earned = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)


class UserResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    anonymous_id = models.CharField(max_length=255, null=True, blank=True)
