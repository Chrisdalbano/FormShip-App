from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.participant import Participant
from ..models.quiz import Quiz
from ..serializers.participant_serializer import ParticipantSerializer
from rest_framework import status
from ..models.quiz_invite import InvitedUser


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
    Expects data like:
      {
        "email": "...",
        "name": "...",
        "password": "...",
        "invitation_token": "...",  (optional)
      }
    We'll validate the quiz's access_control rules, password, etc.
    Returns a participant record or an error.
    """

    quiz_obj = get_object_or_404(Quiz, id=quiz_id)

    # 1) Check if quiz is published or in testing mode – you can decide
    if not quiz_obj.is_published and not quiz_obj.is_testing:
        return Response(
            {"error": "Quiz is not accessible (unpublished)."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # 2) Access control checks
    access_mode = quiz_obj.access_control  # public, invitation, login_required
    user = request.user if request.user.is_authenticated else None

    # 2a) If login_required, the participant must be an authenticated user
    if access_mode == "login_required":
        if not user:
            return Response(
                {"error": "You must be logged in to access this quiz."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    # 2b) If invitation-only, the user must have a valid invite or matching email
    if access_mode == "invitation":
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required for invitation-based quizzes."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invited_exists = InvitedUser.objects.filter(quiz=quiz_obj, email=email).exists()
        if not invited_exists:
            return Response(
                {"error": "This email is not invited to take this quiz."},
                status=status.HTTP_403_FORBIDDEN,
            )

    # 3) If the quiz requires a password, validate it
    if quiz_obj.require_password:
        provided_password = request.data.get("password")
        if provided_password != quiz_obj.password:
            return Response(
                {"error": "Invalid quiz password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    # 4) If the quiz does NOT allow anonymous, we need some form of name or an authenticated user
    allow_anonymous = quiz_obj.allow_anonymous
    require_name = quiz_obj.require_name
    name = request.data.get("name")
    if not allow_anonymous:
        # Must have at least a name or an authenticated user
        if not user and (not name or name.strip() == ""):
            return Response(
                {"error": "Name or authenticated user required (quiz not allowing anonymous)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if require_name and (not name or name.strip() == ""):
        return Response(
            {"error": "A name/nickname is required for this quiz."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 5) Create or retrieve participant
    participant_data = {
        "quiz": quiz_obj.id,
        "name": name if name else None,
        "is_authenticated_user": bool(user),
    }

    # Optionally store the email if invitation or user is logged in
    if access_mode == "invitation":
        participant_data["email"] = request.data.get("email")

    if user and not participant_data.get("email"):
        # If the user is logged in, we can store their user’s email or external ID
        participant_data["email"] = user.email

    serializer = ParticipantSerializer(data=participant_data)
    if serializer.is_valid():
        participant_obj = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)