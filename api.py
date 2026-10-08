from ninja import NinjaAPI
# from ninja_jwt.controller import NinjaJWTDefaultController
# from ninja_jwt.routers.obtain import obtain_pair_router

from routers.admin_auth import router as auth_router
from routers.admin_site_settings import admin_router as site_settings_router  # 引入後台網站設定的路由
from routers.admin_site_settings import public_router as site_settings_router_public  # 引入後台網站設定的路由
from routers.admin_img import router as pictures_router  # 引入後台圖片上傳的路由
from routers.admin_banner import admin_router as admin_banner
from routers.admin_banner import public_router as public_banner
from routers.admin_cashflow import router as cashflow_admin_router
from routers.admin_product import admin_product_router, public_product_router
from routers.admin_clients import router as admin_clients_router
from routers.client_auth_profile import public_client_router, client_profile_router

api = NinjaAPI(
    title="遊戲幣平台 API", 
    version="1.0.0",
    description="包含前台玩家 API 與後台管理員 API"
)
api.add_router("/auth", auth_router)
# api.add_router("/tokens", obtain_pair_router, tags=["Authentication"])
api.add_router("/admin/site", site_settings_router)  # 將後台網站設定的路由加入 API
api.add_router("/public", site_settings_router_public)  # 將後台網站設定的路由加入 API
api.add_router("/admin", pictures_router)  # 將後台圖片上傳的路由加入 API
api.add_router("/admin", admin_banner)  # 將後台網站設定的路由加入 API
api.add_router("/public", public_banner)  # 將後台網站設定的路由加入 API
api.add_router("/admin/cashflow", cashflow_admin_router)
api.add_router("/admin", admin_product_router)
api.add_router("/public", public_product_router)
api.add_router("/admin/clients", admin_clients_router)
api.add_router("/public/clients", public_client_router)
api.add_router("/clients/profile", client_profile_router)



# api.register_controllers(NinjaJWTDefaultController)

