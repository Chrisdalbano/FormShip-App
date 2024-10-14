from django.urls import path, include

# backend/api/urls/__init__.py
from ..views.quiz_views import create_quiz

urlpatterns = [
    path("groups/", include("api.urls.group_urls")),
    path("quizzes/", include("api.urls.quiz_urls")),
    path("questions/", include("api.urls.question_urls")),
    path("users/", include("api.urls.user_urls")),
    path(
        "create-quiz/", create_quiz, name="create_quiz"
    ),  # Directly linking the create_quiz view
]
