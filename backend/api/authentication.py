from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models.participant import Participant

class ParticipantJWTAuthentication(JWTAuthentication):
    user_id_claim = 'participant_id'
    
    def get_user(self, validated_token):
        try:
            participant_id = validated_token.get(self.user_id_claim)
            if not participant_id:
                raise AuthenticationFailed('No participant ID in token')
                
            participant = Participant.objects.get(id=participant_id)
            
            # Ensure the participant is properly authenticated
            if not participant.is_authenticated_user:
                participant.is_authenticated_user = True
                participant.save()
                
            return participant
        except Participant.DoesNotExist:
            raise AuthenticationFailed('Participant not found')
        except Exception as e:
            raise AuthenticationFailed(str(e)) 