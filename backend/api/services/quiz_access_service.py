from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from ..models.quiz import Quiz
from ..models.quiz_invite import InvitedUser
from ..models.participant import QuizParticipation
from ..models.user import AccountMembership

class QuizAccessService:
    @staticmethod
    def check_quiz_access(quiz: Quiz, participant=None, email=None):
        """
        Check if a participant has access to a quiz based on access control settings.
        Returns (has_access, error_message, required_action)
        """
        # FormShip users can access if they're part of the quiz's account
        if hasattr(participant, 'accounts'):
            membership = AccountMembership.objects.filter(
                account=quiz.account,
                user=participant
            ).first()
            if membership:
                return True, None, None
            # If not a member of the quiz's account, treat as regular participant
            participant = None

        # For unpublished quizzes, only FormShip users can access
        if not quiz.is_published:
            return False, "This quiz is not currently available.", "QUIZ_UNAVAILABLE"

        # Public quizzes are accessible to everyone
        if quiz.access_control == "public":
            return True, None, None

        # Login required quizzes need participant authentication
        if quiz.access_control == "login_required":
            if not participant:
                return False, "Please log in or register to access this quiz.", "REQUIRE_AUTH"
            
            # Ensure participant is properly authenticated
            if not participant.is_authenticated_user:
                return False, "Please log in or register to access this quiz.", "REQUIRE_AUTH"
                
            # Create participation record if it doesn't exist
            QuizAccessService.link_participant_to_quiz(participant, quiz)
            return True, None, None

        # Invitation-only quizzes need email verification
        if quiz.access_control == "invitation":
            # If participant is logged in, check their email
            if participant:
                is_invited = InvitedUser.objects.filter(
                    quiz=quiz,
                    email=participant.email,
                    is_active=True
                ).exists()
                if is_invited:
                    return True, None, None
                return False, "You are not invited to take this quiz.", "NOT_INVITED"

            # If no participant, check provided email
            if not email:
                return False, "Please provide your email to verify invitation.", "REQUIRE_EMAIL"
                
            is_invited = InvitedUser.objects.filter(
                quiz=quiz,
                email=email,
                is_active=True
            ).exists()
            
            if not is_invited:
                return False, "You are not invited to take this quiz.", "NOT_INVITED"
            return True, None, None

        # Password protected quizzes need password verification
        if quiz.access_control == "password":
            return False, "Please enter the quiz password.", "REQUIRE_PASSWORD"

        return False, "Invalid access control setting.", "INVALID_SETTING"

    @staticmethod
    def link_participant_to_quiz(participant, quiz):
        """
        Create or get quiz participation for a participant
        """
        # Don't create participations for FormShip users
        if not participant or hasattr(participant, 'accounts'):
            return None

        # Create or get participation
        participation, created = QuizParticipation.objects.get_or_create(
            participant=participant,
            quiz=quiz,
            defaults={
                'has_completed': False,
                'final_score': None
            }
        )

        # If this is a new participation, create any necessary initial state
        if created:
            # You could initialize any required data here
            pass

        return participation

    @staticmethod
    def verify_quiz_password(quiz: Quiz, provided_password: str):
        """
        Verify the password for password-protected quizzes
        """
        if not quiz.require_password:
            return True
            
        if not provided_password:
            raise PermissionDenied("Password is required for this quiz.")
            
        if provided_password != quiz.password:
            raise PermissionDenied("Invalid quiz password.") 