import json
from typing import Optional
from urllib.parse import parse_qs

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

try:
    import jwt  # 可选：PyJWT（如未安装则跳过）
except Exception:  # noqa
    jwt = None

from channels.auth import AuthMiddlewareStack


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


def _validate_token(token: str) -> Optional[dict]:
    """返回 payload（任意结构）表示通过；None 表示失败。支持三种：
    1) 与 WS_SHARED_TOKEN 完全匹配
    2) 'signed:<value>' 使用 Django 签名器校验
    3) 标准 JWT（需安装 PyJWT，HS256，以 SECRET_KEY 校验）
    """
    if not token:
        return None

    # 1) 共享令牌
    if settings.WS_SHARED_TOKEN and token == settings.WS_SHARED_TOKEN:
        return {"method": "shared", "sub": "shared"}

    # 2) 签名 token
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

    # 3) JWT（可选）
    if jwt and token.count(".") == 2:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return {"method": "jwt", **payload}
        except Exception:
            return None

    return None


class TokenAuthMiddleware:
    """为 scope 注入 auth_ok 与 auth_identity；不直接拒绝连接，交由 Consumer 决定。"""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # 先保留 Session/用户（由内部 AuthMiddlewareStack 提供）
        user = scope.get("user", AnonymousUser())
        token = _extract_token(scope)
        identity = _validate_token(token) if token else None

        # 开发环境：允许匿名便于调试
        auth_ok = bool(getattr(user, "is_authenticated", False)) or bool(identity) or bool(settings.DEBUG)

        new_scope = dict(scope)
        new_scope["auth_ok"] = auth_ok
        new_scope["auth_identity"] = identity
        if not new_scope.get("user"):
            new_scope["user"] = user or AnonymousUser()

        return await self.inner(new_scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    # 内层仍保留 Session 鉴权
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
