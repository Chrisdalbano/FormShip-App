from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.participant import Participant, QuizParticipation
from ..models.quiz import Quiz
from ..serializers.participant_serializer import ParticipantSerializer
from rest_framework import status
from ..models.quiz_invite import InvitedUser
from rest_framework.views import APIView
from ..utils.token_generator import generate_participant_token, verify_participant_token
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny
from django.db import models
import jwt
from rest_framework.exceptions import AuthenticationFailed
from ..authentication import ParticipantJWTAuthentication
from ..permissions import IsParticipant, IsQuizParticipant


@api_view(["GET"])
@permission_classes([IsParticipant])
@authentication_classes([ParticipantJWTAuthentication])
def participant_detail(request, participant_id):
    """Get participant details - only accessible by the participant themselves"""
    if str(request.user.id) != participant_id:
        return Response({"error": "Permission denied."}, status=403)
        
    serializer = ParticipantSerializer(request.user)
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


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])  # No authentication required for registration
def participant_register(request):
    """Register a new participant"""
    try:
        data = request.data.copy()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'detail': f'{field} is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check if participant already exists
        if Participant.objects.filter(email=data['email']).exists():
            return Response(
                {'detail': 'A participant with this email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'quiz' not in data:
            data['quiz'] = None
            
        # Remove password from data as we'll set it after creation
        password = data.pop('password')
        
        serializer = ParticipantSerializer(data=data)
        if serializer.is_valid():
            participant = serializer.save()
            participant.set_password(password)
            participant.save()
            
            token = generate_participant_token(participant)
            
            return Response({
                'token': token,
                'participant_id': str(participant.id),
                'name': participant.name,
                'email': participant.email
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'detail': 'Invalid registration data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response(
            {'detail': 'Registration failed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])  # No authentication required for login
def participant_login(request):
    """Handle participant login"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'detail': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            participant = Participant.objects.get(email=email)
            
            if not participant.password:
                return Response(
                    {'detail': 'No password set for this account'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            if participant.check_password(password):
                token = generate_participant_token(participant)
                
                return Response({
                    'token': token,
                    'participant_id': str(participant.id),
                    'name': participant.name,
                    'email': participant.email
                })
            else:
                return Response(
                    {'detail': 'Invalid password'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Participant.DoesNotExist:
            return Response(
                {'detail': 'No account found with this email'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        return Response(
            {'detail': 'An unexpected error occurred'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_participant_from_token(request):
    """Helper function to get participant from token"""
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            print("Invalid auth header format:", auth_header)
            raise AuthenticationFailed('Invalid token format')
            
        token = auth_header.split(' ')[1]
        print(f"Processing token: {token[:20]}...")
        
        try:
            payload = verify_participant_token(token)
            participant = Participant.objects.get(id=payload['participant_id'])
            print(f"Found participant: {participant.email}")
            return participant
        except jwt.ExpiredSignatureError:
            print("Token expired")
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {str(e)}")
            raise AuthenticationFailed('Invalid token')
        except Participant.DoesNotExist:
            print(f"Participant not found for ID: {payload.get('participant_id')}")
            raise AuthenticationFailed('Participant not found')
    except Exception as e:
        print(f"Error getting participant from token: {str(e)}")
        raise AuthenticationFailed(str(e))


@api_view(['GET'])
@permission_classes([IsParticipant])
@authentication_classes([ParticipantJWTAuthentication])
def participant_quizzes(request):
    """Get quizzes for the authenticated participant"""
    try:
        # Get published quizzes or quizzes the participant is specifically invited to
        quizzes = Quiz.objects.filter(
            participations__participant=request.user
        ).filter(
            is_published=True
        ).annotate(
            completed=models.Case(
                models.When(participations__has_completed=True, then=True),
                default=False,
                output_field=models.BooleanField(),
            ),
            final_score=models.F('participations__final_score'),
            completed_at=models.F('participations__responded_at')
        ).values('id', 'title', 'completed', 'final_score', 'completed_at')
        
        return Response(list(quizzes))
        
    except Exception as e:
        return Response(
            {'detail': 'Failed to fetch quizzes'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsParticipant])
@authentication_classes([ParticipantJWTAuthentication])
def get_participant_profile(request):
    """Get authenticated participant's profile"""
    serializer = ParticipantSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsParticipant])
@authentication_classes([ParticipantJWTAuthentication])
def update_participant(request):
    """Update authenticated participant's profile"""
    try:
        participant = request.user
        
        # Update fields
        if 'name' in request.data:
            participant.name = request.data['name']
        if 'email' in request.data:
            if Participant.objects.filter(email=request.data['email']).exclude(id=participant.id).exists():
                return Response(
                    {'detail': 'This email is already in use'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            participant.email = request.data['email']
        if 'password' in request.data:
            participant.set_password(request.data['password'])
        
        participant.save()
        
        return Response({
            'id': str(participant.id),
            'name': participant.name,
            'email': participant.email,
            'created_at': participant.created_at
        })
        
    except Exception as e:
        return Response(
            {'detail': 'Failed to update profile'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsParticipant])
@authentication_classes([ParticipantJWTAuthentication])
def delete_participant(request):
    """Delete authenticated participant's account"""
    try:
        request.user.delete()
        return Response(
            {'detail': 'Account deleted successfully'}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'detail': 'Failed to delete account'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
