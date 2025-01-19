from django.urls import path
from ..views.account_views import (
    create_account,
    transfer_ownership,
    list_account_members,
    invite_member,
    get_account,
    set_password,
    create_user,
    manage_user,  # Unified route for user updates and deletion
)

urlpatterns = [
    path("create/", create_account, name="create_account"),
    path(
        "<int:account_id>/transfer-ownership/",
        transfer_ownership,
        name="transfer_ownership",
    ),
    path(
        "<int:account_id>/members/",
        list_account_members,
        name="list_account_members",
    ),
    path("<int:account_id>/invite/", invite_member, name="invite_member"),
    path("<int:account_id>/", get_account, name="get_account"),
    path("set-password/", set_password, name="set_password"),
    path("<int:account_id>/create-user/", create_user, name="create_user"),
    path(
        "<int:account_id>/users/<str:user_id>/",
        manage_user,
        name="manage_user",
    ),
]
