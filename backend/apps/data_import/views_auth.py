# python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .responses import ok, fail

User = get_user_model()


def _add_to_group(user, group_name: str):
    try:
        grp, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(grp)
    except Exception:
        pass


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """
    注册并直接颁发 JWT
    Body: { "username": "...", "password": "...", "role": "viewer|annotator" }
    """
    username = (request.data.get("username") or "").strip()
    password = (request.data.get("password") or "").strip()
    role = (request.data.get("role") or "viewer").strip().lower()
    if not username or not password:
        return fail("用户名与密码必填", status=400)
    if role not in ["viewer", "annotator"]:
        role = "viewer"

    if User.objects.filter(username=username).exists():
        return fail("用户名已存在", status=400)

    user = User.objects.create_user(username=username, password=password)
    _add_to_group(user, role)

    refresh = RefreshToken.for_user(user)
    data = {
        "user": {
            "id": user.id,
            "username": user.username,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "groups": list(user.groups.values_list("name", flat=True)),
        },
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
    return ok(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    return ok({
        "id": user.id,
        "username": user.username,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "groups": list(user.groups.values_list("name", flat=True)),
    })
