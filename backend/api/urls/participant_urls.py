from django.urls import path
from ..views.participant_views import (
    participant_register,
    participant_login,
    participant_quizzes,
    get_participant_profile,
    update_participant,
    delete_participant
)

urlpatterns = [
    path('register/', participant_register, name='participant-register'),
    path('login/', participant_login, name='participant-login'),
    path('my-quizzes/', participant_quizzes, name='participant-quizzes'),
    path('me/', get_participant_profile, name='get-participant-profile'),
    path('me/update/', update_participant, name='update-participant'),
    path('me/delete/', delete_participant, name='delete-participant'),
]
