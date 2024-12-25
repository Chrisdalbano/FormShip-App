from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ..views.user_views import (
    change_password,
    submit_quiz_results,
    get_quiz_result,
    register_user,
    user_profile,
)

urlpatterns = [
    path("submit-results/", submit_quiz_results, name="submit_quiz_results"),
    path("results/<int:result_id>/", get_quiz_result, name="get_quiz_result"),
    path("register/", register_user, name="register_user"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", user_profile, name="user-profile"),
    path("me/", user_profile, name="user-profile-update"),
    path("change-password/", change_password, name="change-password"),
]
