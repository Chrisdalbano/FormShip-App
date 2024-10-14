# backend/api/urls/question_urls.py

from django.urls import path
from ..views.question_views import question_detail, create_question

urlpatterns = [
    path("<int:question_id>/", question_detail, name="question_detail"),
    path("create/<int:quiz_id>/", create_question, name="create_question"),
]
