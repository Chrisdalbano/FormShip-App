from django.urls import include, path
from ..views.attempt_views import get_attempts

from ..views.quiz_views import (
    list_quizzes,
    create_quiz,
    quiz_detail,
    duplicate_quiz,
    share_quiz,
    move_quiz_to_group,
    update_quiz_order,
)

urlpatterns = [
    path("", list_quizzes, name="list_quizzes"),
    path("create/", create_quiz, name="create_quiz"),
    path("<str:quiz_id>/", quiz_detail, name="quiz_detail"),
    path("<str:quiz_id>/duplicate/", duplicate_quiz, name="duplicate_quiz"),
    path("<str:quiz_id>/share/", share_quiz, name="share_quiz"),
    path("<str:quiz_id>/move-to-group/", move_quiz_to_group, name="move_quiz_to_group"),
    path("update-order/", update_quiz_order, name="update_quiz_order"),
    path("participants/", include("api.urls.participant_urls")),
    path("<str:quiz_id>/attempts/", get_attempts, name="quiz-attempts"),
]
