from rest_framework import serializers
from ..models.question import Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"
        extra_kwargs = {"quiz": {"required": False}}

    def validate(self, data):
        options = [
            data.get("option_a"),
            data.get("option_b"),
            data.get("option_c"),
            data.get("option_d"),
            data.get("option_e"),
        ]
        non_empty_options = [opt for opt in options if opt]
        if len(non_empty_options) < 2:
            raise serializers.ValidationError(
                "A question must have at least two options."
            )
        return data
