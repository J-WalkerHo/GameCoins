from ninja import Schema
from typing import List, Optional


class LoginInSchema(Schema):
    username: str
    password: str

class TokenOutSchema(Schema):
    access: str
    refresh: str
    username: str
    is_staff: bool

class ProductOutSchema(Schema):
    id: int
    name: str
    img_link: str
    trade_type: str
    ratio: float
    moq: float
    max_oq: float
    is_soldout: bool

class CreateOrderInSchema(Schema):
    client_id: int
    product_id: int
    order_price: float  # 玩家打算花多少台幣購買
    game_id: str        # 遊戲伺服器
    game_account: str   # 遊戲角色名稱
    payment_source: str # 選擇的金流管道

class OrderOutSchema(Schema):
    order_id: str
    order_status: str
    order_price: float
    game_coins: float
    payment_info: Optional[str] = None

class NoticeSettingOutSchema(Schema):
    is_notice_enabled: bool
    notice: str
    last_editor: Optional[str] = None
    last_edited_time: Optional[str] = None

class UpdateNoticeInSchema(Schema):
    is_notice_enabled: bool
    notice: str

class UploadImageOutSchema(Schema):
    id: int
    filename: str
    file_link: str
    type: str

class PictureItemOutSchema(Schema):
    id: int
    filename: str
    file_link: str
    type: str

class PictureListResponseSchema(Schema):
    items: List[PictureItemOutSchema]
    total_count: int

class SiteConfigOutSchema(Schema):
    site_name: str
    pc_logo_img: str
    mobile_logo_img: str
    address_logo_img: str
    company_name: str
    company_id: str
    company_phone: str
    company_mail: str
    company_line: str

class UpdateSiteConfigInSchema(Schema):
    site_name: str
    pc_logo_img: str       # 填入圖片上傳 API 回傳的 file_link
    mobile_logo_img: str   # 填入圖片上傳 API 回傳的 file_link
    address_logo_img: str  # 填入圖片上傳 API 回傳的 file_link
    company_name: str
    company_id: str
    company_phone: str
    company_mail: str
    company_line: str
