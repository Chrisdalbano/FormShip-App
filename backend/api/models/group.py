from django.db import models
from .user import Account


class Group(models.Model):

    account = models.ForeignKey(
        Account, related_name="groups", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#FFFFFF")  # Optional color field
    order = models.PositiveIntegerField(default=0)  # Field for managing group order
    created_at = models.DateTimeField(auto_now_add=True)  # New created_at field

    def __str__(self):
        return self.name
