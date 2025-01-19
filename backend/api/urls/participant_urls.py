from django.urls import path
from ..views.participant_views import participant_detail, update_participant_score

urlpatterns = [
    path("<str:participant_id>/", participant_detail, name="participant_detail"),
    path(
        "<str:participant_id>/update-score/",
        update_participant_score,
        name="update_participant_score",
    ),
]
