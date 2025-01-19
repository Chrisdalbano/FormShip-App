from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.participant import Participant
from ..models.quiz import Quiz
from ..serializers.participant_serializer import ParticipantSerializer


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
