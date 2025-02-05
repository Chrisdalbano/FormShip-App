from rest_framework import permissions
from .models.user import AccountMembership

class IsFormShipUser(permissions.BasePermission):
    """
    Permission class for FormShip native users.
    """
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'accounts'))

class IsParticipant(permissions.BasePermission):
    """
    Permission class for external participants.
    """
    def has_permission(self, request, view):
        from .models.participant import Participant
        return bool(request.user and isinstance(request.user, Participant))

class IsQuizOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class for quiz owners or account admins.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False
            
        # Get membership for the quiz's account
        membership = AccountMembership.objects.filter(
            account=obj.account,
            user=request.user
        ).first()
        
        return bool(membership and membership.role in ['owner', 'admin'])

class IsQuizParticipant(permissions.BasePermission):
    """
    Permission class for quiz participants.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not hasattr(request.user, 'final_score'):
            return False
            
        # Check if participant is invited to this quiz
        return obj.participations.filter(participant=request.user).exists()

class CanTestQuiz(permissions.BasePermission):
    """
    Permission class for testing quizzes.
    Allows FormShip users to test their quizzes regardless of publish status.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False
            
        # FormShip users can always test their quizzes
        if hasattr(request.user, 'accounts'):
            membership = AccountMembership.objects.filter(
                account=obj.account,
                user=request.user
            ).first()
            return bool(membership)
            
        # Participants need the quiz to be published
        return obj.is_published 