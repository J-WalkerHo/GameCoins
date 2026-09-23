from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List
from accounts.models import Banner
from routers.admin_auth import admin_auth  # 引入後台驗證器
from schemas import BannerOutSchema, UpdateBannerInSchema, CreateBannerInSchema

admin_router = Router(tags=["後台-Banner設定"], auth=admin_auth)
public_router = Router(tags=["前台-公開資料"])

@admin_router.get("/banners", response=List[BannerOutSchema])
def list_admin_banners(request):
    return Banner.objects.all()

@admin_router.post("/banners", response=BannerOutSchema)
def create_banner(request, payload: CreateBannerInSchema):
    banner = Banner.objects.create(**payload.dict())
    return banner

@admin_router.get("/banners/{banner_id}", response=BannerOutSchema)
def get_banner_detail(request, banner_id: int):
    banner = get_object_or_404(Banner, id=banner_id)
    return banner

@admin_router.put("/banners/{banner_id}", response=BannerOutSchema)
def update_banner(request, banner_id: int, payload: UpdateBannerInSchema):
    banner = get_object_or_404(Banner, id=banner_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(banner, attr, value)
    banner.save()
    return banner

@admin_router.delete("/banners/{banner_id}")
def delete_banner(request, banner_id: int):
    banner = get_object_or_404(Banner, id=banner_id)
    banner.delete()
    return {"message": f"Banner #{banner_id} 已成功刪除"}

@public_router.get("/banners", response=List[BannerOutSchema], auth=None)
def list_public_banners(request):
    """前台首頁獲取開啟中的 Banners 輪播圖 (依 sort_order 排序)"""
    return Banner.objects.filter(is_active=True).order_by('-id')




