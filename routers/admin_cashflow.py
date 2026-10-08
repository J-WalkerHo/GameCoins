from ninja import Router, File, Form
from django.shortcuts import get_object_or_404
from decimal import Decimal
from accounts.models import CashFlowSettings, CashFlowConfig
from routers.admin_auth import admin_auth
from schemas import SupplierOptionOutSchema, CashFlowSettingSchema

router = Router(tags=["後台-金流設定"], auth=admin_auth)

@router.get("/suppliers", response=SupplierOptionOutSchema)
def get_supplier_options(request):
    """
    取得可選擇的金流廠商列表
    """
    config, _ = CashFlowConfig.objects.get_or_create(id=1)

    default_suppliers = ["GSPay", "MMPay", "歐付寶"]
    for supplier in default_suppliers:
        CashFlowSettings.objects.get_or_create(supplier_name=supplier)

    return {
        "active_supplier": str(config.active_supplier),
        "available_suppliers": default_suppliers
        }

# 2. 取得指定金流廠商的詳細參數 (選單切換時呼叫)
@router.get("/settings/{supplier_name}", response=CashFlowSettingSchema)
def get_provider_setting(request, supplier_name: str):
    setting, _ = CashFlowSettings.objects.get_or_create(supplier_name=supplier_name)
    return {
        "supplier_name": setting.supplier_name,
        "env_type": setting.env_type,
        "merchant_id": setting.merchant_id or "",
        "hash_key": setting.hash_key or "",
        "hash_iv": setting.hash_iv or "",
        "has_store_pay": setting.has_store_pay,
        "has_virtual_pay": setting.has_virtual_pay,
        "has_credit_pay": setting.has_credit_pay,
        "has_withdrawal": setting.has_withdrawal,
        "service_fee_fixed": float(setting.service_fee_fixed),
        "service_fee_percent": float(setting.service_fee_percent),
        "service_fee_max": float(setting.service_fee_max),
        "service_fee_min": float(setting.service_fee_min),
        "withdrawal_fee_fixed": float(setting.withdrawal_fee_fixed),
        "withdrawal_fee_percent": float(setting.withdrawal_fee_percent),
    }

# 3. 儲存金流廠商參數與啟用設定 (點擊「儲存」按鈕呼叫)
@router.put("/settings", response=CashFlowSettingSchema)
def update_provider_setting(request, payload: CashFlowSettingSchema):
    # 1. 更新全站預設使用的供應商名稱
    config, _ = CashFlowConfig.objects.get_or_create(id=1)
    config.active_supplier = payload.supplier_name
    config.save()

    # 2. 更新該金流廠商的詳細參數
    setting, _ = CashFlowSettings.objects.get_or_create(supplier_name=payload.supplier_name)
    
    setting.env_type = payload.env_type
    setting.merchant_id = payload.merchant_id
    setting.hash_key = payload.hash_key
    setting.hash_iv = payload.hash_iv

    setting.has_store_pay = payload.has_store_pay
    setting.has_virtual_pay = payload.has_virtual_pay
    setting.has_credit_pay = payload.has_credit_pay
    setting.has_withdrawal = payload.has_withdrawal

    setting.service_fee_fixed = Decimal(str(payload.service_fee_fixed or 0))
    setting.service_fee_percent = Decimal(str(payload.service_fee_percent or 0))
    setting.service_fee_max = Decimal(str(payload.service_fee_max or 0))
    setting.service_fee_min = Decimal(str(payload.service_fee_min or 0))

    setting.withdrawal_fee_fixed = Decimal(str(payload.withdrawal_fee_fixed or 0))
    setting.withdrawal_fee_percent = Decimal(str(payload.withdrawal_fee_percent or 0))

    setting.save()

    return get_provider_setting(request, payload.supplier_name)