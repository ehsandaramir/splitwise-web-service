from rest_framework import permissions


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in ['POST']
