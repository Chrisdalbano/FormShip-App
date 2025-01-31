from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.participant import Participant
from ..models.quiz import Quiz
from ..serializers.participant_serializer import ParticipantSerializer
from rest_framework import status
from ..models.quiz_invite import InvitedUser
from rest_framework.views import APIView


@api_view(["GET"])
def participant_detail(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    serializer = ParticipantSerializer(participant)
    return Response(serializer.data)


@api_view(["POST"])
def update_participant_score(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    new_score = request.data.get("score")
    if new_score is None:
        return Response({"error": "Score is required."}, status=400)

    participant.final_score = new_score
    participant.save()
    return Response({"message": "Score updated successfully."})


@api_view(["POST"])
def create_or_validate_participant(request, quiz_id):
    """
    Handles participant creation or validation for a given quiz.
    Differentiates between internal (account members) and external participants.
    """
    quiz_obj = get_object_or_404(Quiz, id=quiz_id)

    if not quiz_obj.is_published and not quiz_obj.is_testing:
        return Response(
            {"error": "Quiz is not accessible (unpublished or not in testing mode)."},
            status=status.HTTP_403_FORBIDDEN,
        )

    access_mode = quiz_obj.access_control
    user = request.user if request.user.is_authenticated else None

    if access_mode == "login_required" and not user:
        return Response(
            {"error": "Login required to access this quiz."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    email = request.data.get("email")
    if access_mode == "invitation" and not email:
        return Response(
            {"error": "Email is required for invitation-based quizzes."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if (
        access_mode == "invitation"
        and not InvitedUser.objects.filter(quiz=quiz_obj, email=email).exists()
    ):
        return Response(
            {"error": "This email is not invited to take this quiz."},
            status=status.HTTP_403_FORBIDDEN,
        )

    provided_password = request.data.get("password")
    if quiz_obj.require_password and provided_password != quiz_obj.password:
        return Response(
            {"error": "Invalid quiz password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    name = request.data.get("name", "Anonymous")
    participant, created = Participant.objects.get_or_create(
        quiz=quiz_obj,
        email=email if email else None,
        defaults={"name": name, "is_authenticated_user": bool(user)},
    )
    if not created:
        participant.name = name or participant.name
        participant.save()

    return Response(
        {"id": participant.id, "message": "Participant successfully validated."},
        status=status.HTTP_200_OK,
    )


class CreateParticipantView(APIView):
    def post(self, request, quiz_id):
        """Creates a participant for a given quiz."""
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Validate access control
        if (
            quiz.access_control == "login_required"
            and not request.user.is_authenticated
        ):
            return Response(
                {"error": "You must be logged in to access this quiz."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        participant_data = {
            "quiz": quiz.id,
            "name": request.data.get("name", None),
            "email": request.data.get("email", None),
            "is_authenticated_user": request.user.is_authenticated,
        }

        serializer = ParticipantSerializer(data=participant_data)
        if serializer.is_valid():
            participant = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
