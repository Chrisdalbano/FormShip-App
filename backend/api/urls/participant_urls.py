from django.urls import path
from ..views.participant_views import (
    participant_detail,
    update_participant_score,
    create_or_validate_participant,
)

urlpatterns = [
    path("<str:participant_id>/", participant_detail, name="participant_detail"),
    path(
        "<str:participant_id>/update-score/",
        update_participant_score,
        name="update_participant_score",
    ),
    path(
        "quiz/<str:quiz_id>/",
        create_or_validate_participant,
        name="create_or_validate_participant",
    ),
]
