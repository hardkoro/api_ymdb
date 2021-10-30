from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Разрешение на редактирование только админу."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_anonymous:
            return False
        else:
            return request.user.is_admin() | request.user.is_superuser


class IsAdminOrSuperuser(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return request.user.is_admin() | request.user.is_superuser
        return False


class ReviewPermissions(BasePermission):
    def has_permission(self, request, view):
        method = request.method

        if method == 'POST':
            return request.user.is_authenticated

        return True

    def has_object_permission(self, request, view, obj):
        method = request.method
        if (method != 'POST' and method != 'GET'):
            if not request.user.is_anonymous:
                return (
                    request.method in SAFE_METHODS
                    or obj.author == request.user
                    or request.user.is_admin()
                    or request.user.is_moderator()
                )
            return False
        return True


class CommentPermissions(BasePermission):
    def has_permission(self, request, view):
        method = request.method

        if method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        method = request.method
        if (method == 'PATCH' or method == 'DELETE'):
            if not request.user.is_anonymous:
                return (
                    request.method in SAFE_METHODS
                    or obj.author == request.user
                    or request.user.is_admin()
                    or request.user.is_moderator()
                )
            return False
        return True
