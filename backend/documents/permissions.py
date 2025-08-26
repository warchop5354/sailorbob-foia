"""
Permissions for document operations.
"""
from rest_framework import permissions


class CanUploadDocuments(permissions.BasePermission):
    """
    Permission to check if user can upload documents.
    Only moderators and admins can upload.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_upload
        )


class CanManageDocuments(permissions.BasePermission):
    """
    Permission to check if user can manage (edit/delete) documents.
    Only moderators and admins can manage documents.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_manage_documents
        )
    
    def has_object_permission(self, request, view, obj):
        # Admins can manage any document
        if request.user.is_admin:
            return True
        
        # Moderators can manage documents they uploaded
        if request.user.is_moderator and obj.uploaded_by == request.user:
            return True
        
        return False


class CanAccessAdminFeatures(permissions.BasePermission):
    """
    Permission to check if user can access admin features.
    Only moderators and admins can access admin features.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_access_admin
        )