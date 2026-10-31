from rest_framework.permissions import BasePermission

class IsAuthenticatedAndNotSubscribed(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (not request.user.subscription)


class IsAuthenticatedAndSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj