from django.urls import path
from ..views.group_views import (
    group_list,
    group_detail,
    update_group_order,
    rename_group,
    delete_group,
)

urlpatterns = [
    path("", group_list, name="group_list"),
    path("<int:group_id>/", group_detail, name="group_detail"),
    path("update-order/", update_group_order, name="update_group_order"),
    path("<int:group_id>/rename/", rename_group, name="rename_group"),
    path("<int:group_id>/delete/", delete_group, name="delete_group"),
]
