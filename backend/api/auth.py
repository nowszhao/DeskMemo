"""
认证相关 API
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import secrets
import logging

from backend.config import settings

logger = logging.getLogger(__name__)

auth_router = APIRouter()

# 存储会话 token（简单实现，生产环境应使用 Redis）
active_tokens = set()


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: str


class AuthCheckResponse(BaseModel):
    authenticated: bool
    auth_enabled: bool


def verify_token(authorization: Optional[str] = Header(None)) -> bool:
    """验证 token"""
    # 如果未启用认证，直接通过
    if not settings.auth_password:
        return True
    
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证信息")
    
    # 提取 Bearer token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="无效的认证方式")
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的认证格式")
    
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="无效或已过期的 token")
    
    return True


@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录"""
    # 检查是否启用了认证
    if not settings.auth_password:
        return LoginResponse(
            success=True,
            token=None,
            message="认证未启用"
        )
    
    # 验证密码
    if request.password != settings.auth_password:
        logger.warning(f"登录失败：密码错误")
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 生成 token
    token = secrets.token_urlsafe(32)
    active_tokens.add(token)
    
    logger.info(f"用户登录成功，生成 token")
    
    return LoginResponse(
        success=True,
        token=token,
        message="登录成功"
    )


@auth_router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """用户登出"""
    if authorization:
        try:
            scheme, token = authorization.split()
            if token in active_tokens:
                active_tokens.remove(token)
                logger.info(f"用户登出成功")
        except ValueError:
            pass
    
    return {"success": True, "message": "登出成功"}


@auth_router.get("/check", response_model=AuthCheckResponse)
async def check_auth():
    """检查认证状态和是否启用认证"""
    return AuthCheckResponse(
        authenticated=not settings.auth_password,  # 未启用认证时认为已认证
        auth_enabled=bool(settings.auth_password)
    )
