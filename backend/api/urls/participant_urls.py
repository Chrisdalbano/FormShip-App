from django.urls import path
from ..views.participant_views import (
    participant_register,
    participant_login,
    participant_quizzes,
    get_participant_profile,
    update_participant_profile,
    delete_participant_account
)

urlpatterns = [
    path('register/', participant_register, name='participant-register'),
    path('login/', participant_login, name='participant-login'),
    path('my-quizzes/', participant_quizzes, name='participant-quizzes'),
    path('me/', get_participant_profile, name='get-participant-profile'),
    path('me/update/', update_participant_profile, name='update-participant-profile'),
    path('me/delete/', delete_participant_account, name='delete-participant-account'),
]
