from django.urls import path
from ..views.user_views import submit_quiz_results, get_quiz_result

urlpatterns = [
    path("submit-results/", submit_quiz_results, name="submit_quiz_results"),
    path("results/<int:result_id>/", get_quiz_result, name="get_quiz_result"),
]
