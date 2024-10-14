from .group_views import group_list, group_detail, update_group_order
from .quiz_views import (
    list_quizzes,
    create_quiz,
    quiz_detail,
    duplicate_quiz,
    share_quiz,
    move_quiz_to_group,
    update_quiz_order,
)
from .question_views import question_detail, create_question
from .user_views import submit_quiz_results, get_quiz_result

__all__ = [
    "group_list",
    "group_detail",
    "update_group_order",
    "list_quizzes",
    "create_quiz",
    "quiz_detail",
    "duplicate_quiz",
    "share_quiz",
    "move_quiz_to_group",
    "update_quiz_order",
    "question_detail",
    "create_question",
    "submit_quiz_results",
    "get_quiz_result",
]
