from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from .quiz import Quiz
from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.utils.crypto import get_random_string


class UserQuizHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    xp_earned = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History of {self.user.username} for quiz {self.quiz.title}"


class UserResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    nickname = models.CharField(max_length=255, null=True, blank=True)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    anonymous_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        user_name = self.user.username if self.user else self.nickname or "Anonymous"
        return f"Result for {user_name} in quiz {self.quiz.title}"


class Account(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    subscription_plan = models.CharField(max_length=100, default="Free Plan")
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="AccountMembership", related_name="accounts"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_accounts",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="AccountMembership", related_name="accounts"
    )

    def transfer_ownership(self, new_owner):
        self.owner = new_owner
        self.save()


class AccountMembership(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50,
        choices=[("owner", "Owner"), ("admin", "Admin"), ("member", "Member")],
        default="member",
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    last_connected = models.DateTimeField(null=True, blank=True)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)  # Email serves as the unique identifier
    username = models.CharField(
        max_length=150, unique=True, blank=True
    )  # Randomly generated if blank
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    last_connected = models.DateTimeField(null=True, blank=True)

    organization_type = models.CharField(
        max_length=50,
        choices=[
            ("ecommerce", "eCommerce"),
            ("education", "Education"),
            ("medical", "Medical"),
        ],
        blank=True,
        null=True,
    )

    groups = models.ManyToManyField(
        Group,
        related_name="api_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="api_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Generate a random username if it is blank or not provided
        if not self.username:
            self.username = get_random_string(length=12)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
