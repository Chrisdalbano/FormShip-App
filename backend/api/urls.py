# backend/api/urls.py

from django.urls import path
from .views import (
    list_quizzes,
    create_quiz,
    delete_quiz,
    duplicate_quiz,
    share_quiz,
    get_quiz,
)

urlpatterns = [
    path("quizzes/", list_quizzes, name="list_quizzes"),
    path("create-quiz/", create_quiz, name="create_quiz"),
    path("quizzes/<int:quiz_id>/delete/", delete_quiz, name="delete_quiz"),
    path("quizzes/<int:quiz_id>/duplicate/", duplicate_quiz, name="duplicate_quiz"),
    path("quizzes/<int:quiz_id>/share/", share_quiz, name="share_quiz"),
    path("quizzes/<int:quiz_id>/", get_quiz, name="get_quiz"),
]
