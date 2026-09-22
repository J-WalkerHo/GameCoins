from ninja import NinjaAPI
# from ninja_jwt.controller import NinjaJWTDefaultController
# from ninja_jwt.routers.obtain import obtain_pair_router

from routers.admin_auth import router as auth_router
from routers.admin_site_settings import router as site_settings_router  # 引入後台網站設定的路由
from routers.admin_img import router as pictures_router  # 引入後台圖片上傳的路由


api = NinjaAPI(
    title="遊戲幣平台 API", 
    version="1.0.0",
    description="包含前台玩家 API 與後台管理員 API"
)
api.add_router("/auth", auth_router)
# api.add_router("/tokens", obtain_pair_router, tags=["Authentication"])
api.add_router("/admin/site", site_settings_router)  # 將後台網站設定的路由加入 API
api.add_router("/admin/pictures", pictures_router)  # 將後台圖片上傳的路由加入 API
# api.register_controllers(NinjaJWTDefaultController)

