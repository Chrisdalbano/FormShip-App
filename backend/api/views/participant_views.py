from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.participant import Participant
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


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])  # No authentication required for registration
def participant_register(request):
    """Register a new participant"""
    try:
        data = request.data.copy()
        print("\n=== REGISTRATION ATTEMPT ===")
        print(f"[Register] Raw data received: {data}")
        
        # Ensure required fields
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if field not in data:
                print(f"[Register] Missing required field: {field}")
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
            
        # Hash password
        if 'password' in data:
            data['password'] = make_password(data['password'])
            print("[Register] Password hashed successfully")
            
        print("[Register] Validating data with serializer")
        serializer = ParticipantSerializer(data=data)
        
        if serializer.is_valid():
            print("[Register] Data validated successfully")
            participant = serializer.save()
            print(f"[Register] Participant created: {participant.email}")
            print(f"[Register] Participant ID: {participant.id}")
            print(f"[Register] Participant Name: {participant.name}")
            print(f"[Register] Participant Password Set: {bool(participant.password)}")
            
            token = generate_participant_token(participant)
            print("[Register] Token generated successfully")
            
            response_data = {
                'token': token,
                'participant_id': str(participant.id),
                'name': participant.name,
                'email': participant.email
            }
            print("[Register] Registration successful")
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        print(f"[Register] Validation failed: {serializer.errors}")
        return Response({
            'detail': 'Invalid registration data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"[Register] Unexpected error: {str(e)}")
        import traceback
        print(f"[Register] Traceback: {traceback.format_exc()}")
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
        print("\n=== LOGIN ATTEMPT ===")
        print(f"[Login] Raw data received: {request.data}")
        
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            print("[Login] Missing email or password")
            return Response(
                {'detail': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            print(f"[Login] Looking up participant: {email}")
            participant = Participant.objects.get(email=email)
            print(f"[Login] Found participant: {participant.email} (ID: {participant.id})")
            print(f"[Login] Password set: {bool(participant.password)}")
            
            if not participant.password:
                print("[Login] No password set for account")
                return Response(
                    {'detail': 'No password set for this account'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            print("[Login] Verifying password")
            if participant.check_password(password):
                print("[Login] Password verified successfully")
                token = generate_participant_token(participant)
                print("[Login] Token generated successfully")
                
                response_data = {
                    'token': token,
                    'participant_id': str(participant.id),
                    'name': participant.name,
                    'email': participant.email
                }
                print("[Login] Login successful")
                return Response(response_data)
            else:
                print("[Login] Password verification failed")
                return Response(
                    {'detail': 'Invalid password'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Participant.DoesNotExist:
            print(f"[Login] No participant found with email: {email}")
            return Response(
                {'detail': 'No account found with this email'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        print(f"[Login] Unexpected error: {str(e)}")
        import traceback
        print(f"[Login] Traceback: {traceback.format_exc()}")
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
@permission_classes([AllowAny])
@authentication_classes([ParticipantJWTAuthentication])
def participant_quizzes(request):
    """Get quizzes for a participant"""
    try:
        participant = request.user
        if not participant:
            raise AuthenticationFailed('No authenticated participant found')
            
        print(f"Fetching quizzes for participant: {participant.email}")
        
        quizzes = Quiz.objects.filter(participants=participant).annotate(
            completed=models.Case(
                models.When(participants__has_completed=True, then=True),
                default=False,
                output_field=models.BooleanField(),
            ),
            final_score=models.F('participants__final_score'),
            completed_at=models.F('participants__responded_at')
        ).values('id', 'title', 'completed', 'final_score', 'completed_at')
        
        print(f"Found {len(quizzes)} quizzes for participant")
        return Response(list(quizzes))
    except AuthenticationFailed as e:
        print(f"Authentication failed: {str(e)}")
        return Response({'message': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(f"Error in participant_quizzes: {str(e)}")
        return Response(
            {'message': 'Failed to fetch quizzes'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([ParticipantJWTAuthentication])
def get_participant_profile(request):
    """Get participant profile"""
    print("[API] Received request for participant profile")
    print("[API] Headers:", request.headers)
    
    try:
        participant = request.user
        if not participant:
            raise AuthenticationFailed('No authenticated participant found')
            
        print(f"[API] Found participant: {participant.email}")
        
        response_data = {
            'id': str(participant.id),
            'name': participant.name,
            'email': participant.email,
            'created_at': participant.created_at
        }
        print("[API] Returning participant profile")
        return Response(response_data)
        
    except AuthenticationFailed as e:
        print(f"[API] Authentication failed in get_participant_profile: {str(e)}")
        return Response(
            {'message': str(e)}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        print(f"[API] Error in get_participant_profile: {str(e)}")
        return Response(
            {'message': 'Failed to get profile'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_participant_profile(request):
    """Update participant profile"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('Invalid token format')
            
        token = auth_header.split(' ')[1]
        payload = verify_participant_token(token)
        
        # Get participant using the ID from token
        participant = Participant.objects.get(id=payload['participant_id'])

        # Update fields
        if 'name' in request.data:
            participant.name = request.data['name']
        if 'email' in request.data:
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
    except (jwt.InvalidTokenError, Participant.DoesNotExist) as e:
        return Response(
            {'message': str(e)}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_participant_account(request):
    """Delete participant account"""
    try:
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = verify_participant_token(token)
        participant = Participant.objects.get(id=payload['participant_id'])
        participant.delete()
        return Response({
            'message': 'Account deleted successfully'
        })
    except (jwt.InvalidTokenError, Participant.DoesNotExist) as e:
        return Response(
            {'message': str(e)}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
