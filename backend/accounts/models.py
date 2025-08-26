"""
User models for FOIA portal authentication and authorization.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based permissions.
    """
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        MODERATOR = 'mod', 'Moderator'
        USER = 'user', 'User'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        help_text='User role determines access permissions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_moderator(self):
        return self.role in [self.Role.ADMIN, self.Role.MODERATOR]
    
    @property
    def can_upload(self):
        """Check if user can upload documents"""
        return self.is_moderator
    
    @property
    def can_manage_documents(self):
        """Check if user can edit/delete documents"""
        return self.is_moderator
    
    @property
    def can_access_admin(self):
        """Check if user can access admin features"""
        return self.is_moderator
