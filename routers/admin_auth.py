from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.authentication import JWTAuth
from schemas import LoginInSchema, TokenOutSchema

router = Router(tags=["後台-驗證"])


class AdminJWTAuth(JWTAuth):
    """
    專門給後台管理 API 使用的驗證器：
    1. 驗證 JWT Token 是否合法且未過期
    2. 檢查使用者是否為後台管理員 (is_staff)
    """
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if user and (user.is_staff or getattr(user, 'is_super_admin', False)):
            return user
        raise HttpError(403, "權限不足，僅限後台管理員存取")

# 初始化後台專用驗證器實例
admin_auth = AdminJWTAuth()

@router.post("/login", response=TokenOutSchema, auth=None)
def login(request, payload: LoginInSchema):
    """
    管理員 / 使用者登入取得 JWT Token
    (在 Swagger UI 上可直接輸入 username 與 password 進行測試)
    """
    # 驗證帳號密碼
    user = authenticate(username=payload.username, password=payload.password)
    
    if not user:
        raise HttpError(401, "帳號或密碼錯誤")
        
    if not user.is_active:
        raise HttpError(403, "此帳號已被停用")

    # 手動簽發 JWT Token
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username,
        "is_staff": user.is_staff
            }