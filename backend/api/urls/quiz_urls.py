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
    log_quiz_event,
    submit_quiz,
    update_quiz_status,
    get_quiz,
    verify_quiz_access,
)

urlpatterns = [
    path("", list_quizzes, name="list_quizzes"),
    path("create/", create_quiz, name="create_quiz"),
    path("update-order/", update_quiz_order, name="update_quiz_order"),
    path("participants/", include("api.urls.participant_urls")),
    
    # Quiz-specific routes
    path("<str:quiz_id>/", get_quiz, name="get-quiz"),  # This should be the main quiz view
    path("<str:quiz_id>/details/", quiz_detail, name="quiz_detail"),  # Admin/management details
    path("<str:quiz_id>/duplicate/", duplicate_quiz, name="duplicate_quiz"),
    path("<str:quiz_id>/share/", share_quiz, name="share_quiz"),
    path("<str:quiz_id>/move-to-group/", move_quiz_to_group, name="move_quiz_to_group"),
    path("<str:quiz_id>/attempts/", get_attempts, name="quiz-attempts"),
    path("<str:quiz_id>/log/", log_quiz_event, name="log_quiz_event"),
    path("<str:quiz_id>/submit/", submit_quiz, name="submit_quiz"),
    path("<str:quiz_id>/update-status/", update_quiz_status, name="update_quiz_status"),
    path("<str:quiz_id>/verify-access/", verify_quiz_access, name="verify-quiz-access"),
]
