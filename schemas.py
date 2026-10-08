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

class BannerOutSchema(Schema):
    id: int
    pc_banner_img: str
    mobile_banner_img: str
    banner_link: Optional[str] = None
    # title: Optional[str] = None
    # sort_order: int
    # is_active: bool

class CreateBannerInSchema(Schema):
    pc_banner_img: str
    mobile_banner_img: str
    banner_link: Optional[str] = None
    # title: Optional[str] = None
    # sort_order: int = 0
    # is_active: bool = True

class UpdateBannerInSchema(Schema):
    pc_banner_img: Optional[str] = None
    mobile_banner_img: Optional[str] = None
    banner_link: Optional[str] = None
    # title: Optional[str] = None
    # sort_order: Optional[int] = None
    # is_active: Optional[bool] = None

class SupplierOptionOutSchema(Schema):
    active_supplier: str
    available_suppliers: List[str]

class CashFlowSettingSchema(Schema):
    supplier_name: str
    env_type: str  # test, prod
    merchant_id: Optional[str] = ""
    hash_key: Optional[str] = ""
    hash_iv: Optional[str] = ""
    
    # 通道開關
    has_store_pay: bool
    has_virtual_pay: bool
    has_credit_pay: bool
    has_withdrawal: bool

    # 收款服務費
    service_fee_fixed: Optional[float] = 0.0
    service_fee_percent: Optional[float] = 0.0
    service_fee_max: Optional[float] = 0.0
    service_fee_min: Optional[float] = 0.0

    # 出款服務費
    withdrawal_fee_fixed: Optional[float] = 0.0
    withdrawal_fee_percent: Optional[float] = 0.0

class ProductOutSchema(Schema):
    id: int
    img_link: Optional[str] = None
    name: str
    trade_type: str                     # sell (出售), buy (收購)
    game_type: Optional[str] = None
    ratio: float                  # 匯率比值 (如 1:100)
    moq: int       # 起購數量
    max_oq: int       # 起購數量
    exclusive_client: Optional[int] = None
    single_digits_allowed: bool
    is_active: bool
    is_soldout: bool

class ProductListResponseSchema(Schema):
    data: List[ProductOutSchema]
    total_count: int

class CreateProductInSchema(Schema):
    img_link: Optional[str] = None
    name: str
    trade_type: str = "sell"
    game_type: Optional[str] = None
    ratio: float = 1.0
    moq: int = 1
    max_oq: int = 10000
    exclusive_client: Optional[int] = None
    single_digits_allowed: bool = False
    is_active: bool = True
    is_soldout: bool = False

class UpdateProductInSchema(Schema):
    img_link: Optional[str] = None
    name: Optional[str] = None
    trade_type: Optional[str] = None
    game_type: Optional[str] = None
    ratio: Optional[float] = None
    moq: Optional[int] = None
    max_oq: Optional[int] = None
    exclusive_client: Optional[int] = None
    single_digits_allowed: Optional[bool] = None
    is_active: Optional[bool] = None
    is_soldout: Optional[bool] = None

class BatchUpdateRatioInSchema(Schema):
    product_ids: List[int]
    ratio: float

class BankAccountOutSchema(Schema):
    id: int
    bank_name: str
    account_number: str
    passbook_img: Optional[str] = None
    account_holder_name: str
    is_verified: bool
    created_at: str

class GameAccountOutSchema(Schema):
    id: int
    game_name: str
    game_id: str
    character_name: str

class ClientDetailOutSchema(Schema):
    id: int
    account: str
    name: str
    id_code: str
    id_verified: bool
    phonenumber: str
    email: str
    registered_at: str
    is_active: bool
    is_tradable: bool

class ClientDetailOutSchema(Schema):
    id: int
    account: str
    name: str
    id_code: str
    id_verified: bool
    phonenumber: str
    email: str
    registered_at: str
    is_active: bool
    is_tradable: bool
    
    # 支付權限開關
    shop_payment: bool
    virtual_account_payment: bool
    credit_card_payment: bool
    
    # 證件照
    idcard_front_img: Optional[str] = None
    idcard_back_img: Optional[str] = None
    
    # 一對多關聯列表
    bank_accounts: List[BankAccountOutSchema]
    game_accounts: List[GameAccountOutSchema]
    
    # 紀錄
    banned_records: List[dict]
    unbanned_records: List[dict]

class ClientListResponseSchema(Schema):
    items: List[ClientDetailOutSchema]
    total_count: int

class ToggleActiveStatusInSchema(Schema):
    is_active: bool
    reason: Optional[str] = "管理員操作"

class VerifyBankInSchema(Schema):
    is_verified: bool

class VerifyIdInSchema(Schema):
    id_verified: bool


class ClientRegisterInSchema(Schema):
    account: str
    password: str
    name: str
    id_code: str
    phonenumber: str
    email: str

class AddGameAccountInSchema(Schema):
    game_name: str
    game_id: str
    character_name: str

class AddBankAccountInSchema(Schema):
    bank_name: str
    account_number: str
    account_holder_name: str