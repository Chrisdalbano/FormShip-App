# backend/api/urls.py

from django.urls import path
from .views import (
    list_quizzes,
    create_quiz,
    quiz_detail,
    question_detail,
    create_question,
    group_detail,
    group_list,
    move_quiz_to_group,
    update_quiz_order,
    update_group_order,
    submit_quiz_results,
)

urlpatterns = [
    path("quizzes/", list_quizzes, name="list_quizzes"),
    path("create-quiz/", create_quiz, name="create_quiz"),
    path("quizzes/<int:quiz_id>/", quiz_detail, name="quiz_detail"),
    path("questions/<int:question_id>/", question_detail, name="question_detail"),
    path("quizzes/<int:quiz_id>/questions/", create_question, name="create_question"),
    path("groups/", group_list, name="group_list"),
    path("groups/<int:group_id>/", group_detail, name="group_detail"),
    path(
        "move-quiz-to-group/<int:quiz_id>/",
        move_quiz_to_group,
        name="move_quiz_to_group",
    ),
    path("update-quiz-order/", update_quiz_order, name="update_quiz_order"),
    path("update-group-order/", update_group_order, name="update_group_order"),
    path("submit-quiz-results/", submit_quiz_results, name="submit_quiz_results"),
]
