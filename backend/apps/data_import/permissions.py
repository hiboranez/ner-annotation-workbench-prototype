from rest_framework.permissions import BasePermission, SAFE_METHODS


def _in_group(user, group_name: str) -> bool:
    try:
        return bool(user and user.is_authenticated and user.groups.filter(name=group_name).exists())
    except Exception:
        return False


def _is_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser or _in_group(user, "admin")))


class IsAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return _is_admin(request.user)


class IsAnnotatorOrAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return _is_admin(user) or _in_group(user, "annotator")


class IsViewerOrAboveReadOnly(BasePermission):
    """
    viewer/annotator/admin 均可，只读。
    """

    def has_permission(self, request, view) -> bool:
        if request.method not in SAFE_METHODS:
            return False
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return _is_admin(user) or _in_group(user, "annotator") or _in_group(user, "viewer")
