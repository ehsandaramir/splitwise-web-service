from rest_framework import permissions


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in ['POST']:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        return False
