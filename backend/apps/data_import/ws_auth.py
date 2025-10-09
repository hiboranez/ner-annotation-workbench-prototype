import json
from typing import Optional
from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

# SimpleJWT
try:
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken
except Exception:  # noqa
    JWTAuthentication = None
    InvalidToken = Exception  # type: ignore


def _get_header(scope, key: str) -> Optional[str]:
    key = key.lower().encode()
    for k, v in scope.get("headers", []):
        if k == key:
            try:
                return v.decode()
            except Exception:
                return None
    return None


def _extract_token(scope) -> Optional[str]:
    # 优先 Authorization: Bearer xxx
    auth = _get_header(scope, "authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    # 其次 query ?token=xxx
    raw_qs = scope.get("query_string", b"")
    try:
        qs = parse_qs(raw_qs.decode())
    except Exception:
        qs = {}
    token = qs.get("token", [None])[0]
    return token


def _authenticate_jwt_user(token: str):
    """
    使用 SimpleJWT 校验并返回 (user, payload)；失败返回 (None, None)
    """
    if not token or not JWTAuthentication:
        return None, None
    try:
        jwt_auth = JWTAuthentication()
        validated = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated)
        payload = {"method": "jwt", "sub": getattr(user, "pk", None)}
        return user, payload
    except InvalidToken:
        return None, None
    except Exception:
        return None, None


def _validate_shared_or_signed(token: str) -> Optional[dict]:
    """
    兼容共享令牌/签名令牌（可选）
    """
    if not token:
        return None

    if settings.WS_SHARED_TOKEN and token == settings.WS_SHARED_TOKEN:
        return {"method": "shared", "sub": "shared"}

    if token.startswith("signed:"):
        value = token.split("signed:", 1)[1]
        signer = TimestampSigner()
        try:
            data = signer.unsign(value, max_age=settings.WS_TOKEN_MAX_AGE)
            try:
                return json.loads(data)
            except Exception:
                return {"method": "signed", "sub": str(data)}
        except (BadSignature, SignatureExpired):
            return None

    return None


class TokenAuthMiddleware:
    """
    从 Header/Query 中提取 Bearer Token：
    - 优先使用 SimpleJWT 验证并设置 scope.user
    - 次选共享/签名 token 仅用于标记 identity，不设置 user
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        base_user = scope.get("user", AnonymousUser())
        token = _extract_token(scope)

        user = base_user or AnonymousUser()
        identity = None

        if token:
            jwt_user, identity = _authenticate_jwt_user(token)
            if jwt_user:
                user = jwt_user
            else:
                identity = _validate_shared_or_signed(token)

        auth_ok = bool(getattr(user, "is_authenticated", False)) or bool(identity) or bool(settings.DEBUG)

        new_scope = dict(scope)
        new_scope["auth_ok"] = auth_ok
        new_scope["auth_identity"] = identity
        new_scope["user"] = user or AnonymousUser()

        return await self.inner(new_scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
