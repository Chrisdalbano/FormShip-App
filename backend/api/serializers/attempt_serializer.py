from rest_framework import serializers
from ..models.attempt import Attempt


class AttemptSerializer(serializers.ModelSerializer):
    # Include participant-related fields
    participant_name = serializers.CharField(
        source="participant.name", default="Anonymous"
    )
    participant_id = serializers.UUIDField(source="participant.id", default=None)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "participant_id",
            "participant_name",
            "score",
            "completed_at",
            "needs_manual_grading",
        ]
