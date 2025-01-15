from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import status
from ..models.group import Group

from ..serializers.group_serializer import GroupSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def group_list(request):
    account = request.user.accounts.first()
    if not account:
        return Response(
            {"error": "No account associated with the user."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if request.method == "GET":
        groups = Group.objects.filter(account=account).order_by("order")
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        # Add account to the request data before serialization
        request.data["account"] = account.id  # Add account ID explicitly
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def group_detail(request, group_id):
    """
    Handles retrieving, updating (name and color), and deleting a group.
    """
    group = get_object_or_404(Group, pk=group_id)

    if request.method == "GET":
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    elif request.method == "PUT":
        # Allow partial updates for name and color fields
        serializer = GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["PUT"])
def update_group_order(request):
    try:
        group_orders = request.data.get("group_orders", [])
        for group_data in group_orders:
            group = Group.objects.get(id=group_data["id"])
            group.order = group_data["order"]
            group.save()
        return Response(status=status.HTTP_200_OK)
    except Group.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def rename_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    new_name = request.data.get("name")
    if new_name:
        group.name = new_name
        group.save()
    serializer = GroupSerializer(group)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Ungroup all quizzes in the group before deleting
    for quiz in group.quizzes.all():
        quiz.group = None
        quiz.save()

    group.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
