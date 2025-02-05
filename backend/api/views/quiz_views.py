import os
from django.conf import settings
from django.http import JsonResponse
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..services.quiz_creation_service import QuizCreationService, QuizCreationError
from openai import OpenAI
from ..models.user import AccountMembership
from ..models.participant import Participant, QuizParticipation
from ..models.quiz import Quiz, SharedQuiz, QuizEventLog, QuizSubmission
from ..models.group import Group
from ..models.question import Question
from ..serializers.quiz_serializer import (
    QuizSerializer, 
    SharedQuizSerializer,
    InvitedUserSerializer,
    QuizSubmissionSerializer
)
from ..serializers.question_serializer import QuestionSerializer
from ..models.quiz_invite import InvitedUser
from ..authentication import ParticipantJWTAuthentication
from ..permissions import (
    IsFormShipUser,
    IsParticipant,
    IsQuizOwnerOrAdmin,
    IsQuizParticipant,
    CanTestQuiz
)
from ..services.quiz_access_service import QuizAccessService

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@api_view(["GET", "POST"])
@permission_classes([IsFormShipUser])
def list_quizzes(request):
    """
    GET: Lists quizzes belonging to the user's account (with optional group filters).
    POST: Creates a new quiz.
    """
    if request.method == "GET":
        account = request.user.accounts.first()
        if not account:
            return Response(
                {"error": "No account associated with this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quizzes = Quiz.objects.filter(account=account)

        # Optional filters
        group_id = request.query_params.get("group_id", None)
        if group_id:
            quizzes = quizzes.filter(group__id=group_id)

        grouped = request.query_params.get("grouped", None)
        if grouped is not None:
            if grouped.lower() in ["false", "null"]:
                quizzes = quizzes.filter(group__isnull=True)
            elif grouped.lower() == "true":
                quizzes = quizzes.filter(group__isnull=False)

        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        return create_quiz(request)


@api_view(["POST"])
@permission_classes([IsFormShipUser])
def create_quiz(request):
    """Creates a new quiz, optionally leveraging AI to generate questions."""
    account = request.user.accounts.first()
    if not account:
        return Response(
            {"error": "No account associated with this user."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    service = QuizCreationService(openai_client=client)

    try:
        quiz_obj, question_objs = service.create_quiz_with_ai(account, request.data)
        quiz_serializer = QuizSerializer(quiz_obj)
        question_serializer = QuestionSerializer(question_objs, many=True)
        data_out = {
            "quiz": quiz_serializer.data,
            "questions": question_serializer.data,
            "id": quiz_obj.id,
        }
        return Response(data_out, status=status.HTTP_201_CREATED)

    except (ValueError, QuizCreationError) as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response(
            {"error": f"Unexpected server error: {str(exc)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsFormShipUser | IsParticipant])
@authentication_classes([JWTAuthentication, ParticipantJWTAuthentication])
def quiz_detail(request, quiz_id):
    """
    GET: Retrieve quiz details (accessible by both FormShip users and participants)
    PUT: Update quiz (FormShip users only)
    DELETE: Delete quiz (FormShip users only)
    """
    quiz_obj = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "GET":
        # Check permissions based on user type
        if hasattr(request.user, 'accounts'):
            # FormShip user - check account membership
            membership = AccountMembership.objects.filter(
                account=quiz_obj.account, user=request.user
            ).first()
            if not membership:
                return Response({"error": "Permission denied."}, status=403)
        else:
            # Participant - check if invited and quiz is published
            if not quiz_obj.is_published and not quiz_obj.participations.filter(participant=request.user).exists():
                return Response({"error": "This quiz is not available."}, status=403)

        serializer = QuizSerializer(quiz_obj)
        return Response(serializer.data)

    elif request.method in ["PUT", "DELETE"]:
        # Only FormShip users with owner/admin role can modify
        if not hasattr(request.user, 'accounts'):
            return Response({"error": "Permission denied."}, status=403)
            
        membership = AccountMembership.objects.filter(
            account=quiz_obj.account, user=request.user
        ).first()
        if not membership or membership.role not in ["owner", "admin"]:
            return Response({"error": "Permission denied."}, status=403)

        if request.method == "PUT":
            serializer = QuizSerializer(quiz_obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            # Handle question updates if present
            questions_data = request.data.get("questions", [])
            if questions_data:
                updated_questions = []
                for q_item in questions_data:
                    q_id = q_item.get("id")
                    if q_id:
                        try:
                            existing_q = quiz_obj.questions.get(id=q_id)
                            q_serializer = QuestionSerializer(
                                existing_q, data=q_item, partial=True
                            )
                            if q_serializer.is_valid():
                                q_serializer.save()
                                updated_questions.append(q_serializer.data)
                        except Question.DoesNotExist:
                            continue
                    else:
                        q_item["quiz"] = quiz_obj.id
                        new_q_serializer = QuestionSerializer(data=q_item)
                        if new_q_serializer.is_valid():
                            new_q_obj = new_q_serializer.save()
                            updated_questions.append(QuestionSerializer(new_q_obj).data)

            updated_quiz_serializer = QuizSerializer(quiz_obj)
            return Response(updated_quiz_serializer.data)

        else:  # DELETE
            quiz_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def duplicate_quiz(request, quiz_id):
    """
    Duplicate an existing quiz and all its questions.
    Optionally ensure user is the owner or has permission.
    """
    original_quiz = get_object_or_404(Quiz, id=quiz_id)

    # (Optional) check ownership if you want
    # if original_quiz.account.owner != request.user:
    #     return Response({"error": "Permission denied."}, status=403)

    # Create the new quiz
    duplicated_quiz = Quiz.objects.create(
        account=original_quiz.account,
        title=f"Copy of {original_quiz.title}",
        topic=original_quiz.topic,
        difficulty=original_quiz.difficulty,
        question_count=original_quiz.question_count,
        quiz_type=original_quiz.quiz_type,
        group=original_quiz.group,
        display_results=original_quiz.display_results,
        require_password=original_quiz.require_password,
        password=original_quiz.password,
        allow_anonymous=original_quiz.allow_anonymous,
        require_name=original_quiz.require_name,
        is_timed=original_quiz.is_timed,
        quiz_time_limit=original_quiz.quiz_time_limit,
        are_questions_timed=original_quiz.are_questions_timed,
        time_per_question=original_quiz.time_per_question,
        skippable_questions=original_quiz.skippable_questions,
        segment_steps=original_quiz.segment_steps,
        allow_previous_questions=original_quiz.allow_previous_questions,
        evaluation_type=original_quiz.evaluation_type,
        is_testing=original_quiz.is_testing,
        is_published=original_quiz.is_published,
        access_control=original_quiz.access_control,
    )

    # Duplicate the questions
    for old_q in original_quiz.questions.all():
        Question.objects.create(
            quiz=duplicated_quiz,
            question_text=old_q.question_text,
            option_a=old_q.option_a,
            option_b=old_q.option_b,
            option_c=old_q.option_c,
            option_d=old_q.option_d,
            option_e=old_q.option_e,
            correct_answer=old_q.correct_answer,
        )

    serializer = QuizSerializer(duplicated_quiz)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def share_quiz(request, quiz_id):
    base_url = settings.BASE_URL  # Define BASE_URL in your settings
    shareable_link = f"{base_url}/quiz/{quiz_id}/"
    return JsonResponse({"shareable_link": shareable_link})


@api_view(["PUT"])
def move_quiz_to_group(request, quiz_id):
    """
    Move a quiz to a new group or ungroup it (group_id=null).
    """
    quiz_obj = get_object_or_404(Quiz, id=quiz_id)
    group_id = request.data.get("group_id")

    if group_id:
        group = get_object_or_404(Group, id=group_id)
        quiz_obj.group = group
    else:
        quiz_obj.group = None

    quiz_obj.order = request.data.get("order", quiz_obj.order)
    quiz_obj.save()

    serializer = QuizSerializer(quiz_obj)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_quiz_order(request):
    """
    Batch update quiz .order for drag-and-drop reordering, e.g.:
    {
      "quiz_orders": [
        {"id": 1, "order": 10},
        {"id": 2, "order": 20}
      ]
    }
    """
    quiz_orders = request.data.get("quiz_orders", [])
    for q_item in quiz_orders:
        q_id = q_item.get("id")
        new_order = q_item.get("order")
        if q_id is not None and new_order is not None:
            try:
                quiz_obj = Quiz.objects.get(id=q_id)
                quiz_obj.order = new_order
                quiz_obj.save()
            except Quiz.DoesNotExist:
                pass  # or handle error
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_users_to_quiz(request, quiz_id):
    """
    If a quiz has access_control='invitation', we can invite external emails to it.
    """
    quiz_obj = get_object_or_404(Quiz, id=quiz_id)

    # Check ownership or admin membership, etc.
    if quiz_obj.account.owner != request.user:
        return Response({"error": "No permission."}, status=status.HTTP_403_FORBIDDEN)

    if quiz_obj.access_control != "invitation":
        return Response(
            {"error": "Quiz is not in invitation-only mode."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    emails = request.data.get("emails", [])
    invited = []
    for email in emails:
        # Insert or get an invited user record
        invited_user, _ = InvitedUser.objects.get_or_create(quiz=quiz_obj, email=email)
        invited.append(invited_user)

    serializer = InvitedUserSerializer(invited, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def log_quiz_event(request, quiz_id):
    """
    Logs quiz-related events like navigation, time spent, and other interactions.
    """
    quiz = Quiz.objects.filter(id=quiz_id).first()
    if not quiz:
        return Response({"error": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

    event_type = request.data.get("type")
    details = request.data.get("details", {})
    participant_id = request.data.get("participant_id", None)

    if not event_type:
        return Response(
            {"error": "Event type is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create the log entry
        QuizEventLog.objects.create(
            quiz=quiz,
            event_type=event_type,
            details=details,
            participant_id=participant_id,
            timestamp=now(),
        )
        return Response(
            {"message": "Event logged successfully."}, status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@permission_classes([IsFormShipUser & IsQuizOwnerOrAdmin])
def update_quiz_status(request, quiz_id):
    """Update quiz status (publish/unpublish)"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    status_action = request.data.get("action")
    if status_action not in ["publish", "unpublish"]:
        return Response(
            {"error": "Invalid action. Use 'publish' or 'unpublish'."},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    quiz.is_published = status_action == "publish"
    quiz.save()
    
    return Response(QuizSerializer(quiz).data)


class QuizViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD operations for quizzes.
    """

    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


@api_view(['POST'])
def validate_invitation(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    email = request.data.get('email')
    
    # Check if email is in invited users
    is_invited = InvitedUser.objects.filter(
        quiz=quiz,
        email=email,
        is_active=True
    ).exists()
    
    return Response({'valid': is_invited})


@api_view(['POST'])
def add_invitations(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    emails = request.data.get('emails', [])
    
    created_invites = []
    for email in emails:
        invite, created = InvitedUser.objects.get_or_create(
            quiz=quiz,
            email=email
        )
        if created:
            created_invites.append(invite)
    
    serializer = InvitedUserSerializer(created_invites, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsFormShipUser | (IsParticipant & IsQuizParticipant)])
def submit_quiz(request, quiz_id):
    """Submit quiz answers - available to both FormShip users (testing) and participants"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Handle FormShip users (testing mode)
    if hasattr(request.user, 'accounts'):
        if not CanTestQuiz().has_object_permission(request, None, quiz):
            return Response({"error": "Permission denied."}, status=403)
    # Handle participants
    else:
        if not quiz.is_published and not IsQuizParticipant().has_object_permission(request, None, quiz):
            return Response({"error": "This quiz is not available."}, status=403)
    
    serializer = QuizSubmissionSerializer(data=request.data)
    if serializer.is_valid():
        submission = serializer.save(
            quiz=quiz,
            participant=request.user if hasattr(request.user, 'final_score') else None
        )
        return Response(QuizSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_quiz(request, quiz_id):
    """
    Get quiz details with access control
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Get participant from token if available
    participant = None
    if 'Authorization' in request.headers:
        try:
            # Try participant authentication first
            auth = ParticipantJWTAuthentication()
            participant = auth.authenticate(request)[0]
        except Exception:
            # If participant auth fails, try FormShip user auth
            try:
                auth = JWTAuthentication()
                participant = auth.authenticate(request)[0]
            except Exception:
                pass
    
    # Check access using service
    has_access, error_message, required_action = QuizAccessService.check_quiz_access(
        quiz=quiz,
        participant=participant,
        email=request.query_params.get('email')
    )
    
    if not has_access:
        response_data = {
            'detail': error_message,
            'required_action': required_action,
            'quiz_title': quiz.title,
            'access_control': quiz.access_control,
            'is_published': quiz.is_published
        }
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)
    
    # If we have a participant and they have access, link them to the quiz
    if participant and not hasattr(participant, 'accounts'):
        QuizAccessService.link_participant_to_quiz(participant, quiz)
    
    # Use different serializers based on user type
    if hasattr(participant, 'accounts'):
        # FormShip user gets full quiz details
        serializer = QuizSerializer(quiz, context={'request': request})
    else:
        # Participant gets limited quiz details
        serializer = QuizSerializer(quiz, context={'request': request})
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_quiz_access(request, quiz_id):
    """
    Verify access requirements for a quiz (password, invitation, etc)
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Handle password verification
    if quiz.access_control == 'password':
        try:
            QuizAccessService.verify_quiz_password(quiz, request.data.get('password'))
            return Response({'detail': 'Access granted'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
            
    # Handle invitation verification
    if quiz.access_control == 'invitation':
        email = request.data.get('email')
        has_access, error_message, _ = QuizAccessService.check_quiz_access(
            quiz=quiz,
            email=email
        )
        if has_access:
            return Response({'detail': 'Invitation verified'})
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
        
    return Response({'detail': 'Invalid verification request'}, status=status.HTTP_400_BAD_REQUEST)
