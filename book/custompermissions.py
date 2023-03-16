from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool((request.user == obj.owner and request.user.is_staff) or
                    (request.user.is_staff and request.user.is_superuser))
        # return bool(request.user.is_staff and request.user.is_superuser)

