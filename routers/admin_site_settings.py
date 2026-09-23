import time, requests
from datetime import datetime, timedelta, timezone

from ninja import Router
from django.shortcuts import get_object_or_404
from typing import Optional
from accounts.models import SiteSettings
from routers.admin_auth import admin_auth  # 引入後台驗證器
from schemas import NoticeSettingOutSchema, UpdateNoticeInSchema, SiteConfigOutSchema, UpdateSiteConfigInSchema

admin_router = Router(tags=["後台-網站設定"], auth=admin_auth)
public_router = Router(tags=["前台-公開資料"])

TW_TZ = timezone(timedelta(hours=8))

@admin_router.get("/notice", response=NoticeSettingOutSchema, auth=admin_auth)
def get_notice_setting(request):

    settings, _ = SiteSettings.objects.get_or_create(id=1)
    return {
        "is_notice_enabled": settings.is_notice_enabled,
        "notice": settings.notice or "",
        "last_editor": settings.last_editor or "",
        "last_edited_time":  settings.last_edited_time.astimezone(TW_TZ).strftime("%Y-%m-%d %H:%M:%S") if settings.last_edited_time else None
    }

@admin_router.put("/notice", response=NoticeSettingOutSchema, auth=admin_auth)
def update_notice_setting(request, payload: UpdateNoticeInSchema):
    setting, _ = SiteSettings.objects.get_or_create(id=1)

    setting.is_notice_enabled = payload.is_notice_enabled
    setting.notice = payload.notice

    setting.last_editor = request.user.username if hasattr(request.user, 'username') else str(request.user)
    setting.last_edited_time = datetime.now()
    tw_time = setting.last_edited_time.astimezone(TW_TZ)
    setting.save()

    return {
        "is_notice_enabled": setting.is_notice_enabled,
        "notice": setting.notice,
        "last_editor": setting.last_editor,
        "last_edited_time": tw_time.strftime("%Y-%m-%d %H:%M:%S")
    }

@public_router.get("/notice")
def get_public_notice(request):
    settings = SiteSettings.objects.first()
    if settings and settings.is_notice_enabled:
        return{
            "enabled": True,
            "notice": settings.notice or ""
        }
    return {
        "enabled": False, "notice": ""
    }

@admin_router.get("/config", response=SiteConfigOutSchema, auth=admin_auth)
def get_site_confing(request):
    settings, _ = SiteSettings.objects.get_or_create(id=1)
    return{
        "site_name": settings.site_name or "",
        "pc_logo_img": settings.pc_logo_img or "",
        "mobile_logo_img": settings.mobile_logo_img or "",
        "address_logo_img": settings.address_logo_img or "",
        "company_name": settings.company_name or "",
        "company_id": settings.company_id or "",
        "company_phone": settings.company_phone or "",
        "company_mail": settings.company_mail or "",
        "company_line": settings.company_line or ""
    }

@admin_router.put("/config", response=SiteConfigOutSchema, auth=admin_auth)
def update_site_config(request, payload: UpdateSiteConfigInSchema):
    setting, _ = SiteSettings.objects.get_or_create(id=1)
    
    setting.site_name = payload.site_name
    setting.pc_logo_img = payload.pc_logo_img
    setting.mobile_logo_img = payload.mobile_logo_img
    setting.address_logo_img = payload.address_logo_img
    setting.company_name = payload.company_name
    setting.company_id = payload.company_id
    setting.company_phone = payload.company_phone
    setting.company_mail = payload.company_mail
    setting.company_line = payload.company_line

    setting.save()

    return{
        "site_name": setting.site_name or "",
        "pc_logo_img": setting.pc_logo_img or "",
        "mobile_logo_img": setting.mobile_logo_img or "",
        "address_logo_img": setting.address_logo_img or "",
        "company_name": setting.company_name or "",
        "company_id": setting.company_id or "",
        "company_phone": setting.company_phone or "",
        "company_mail": setting.company_mail or "",
        "company_line": setting.company_line or ""
    }