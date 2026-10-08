from ninja import Router, File, Form
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from decimal import Decimal
from accounts.models import Client, ClientBankAccount, ClientGameAccount
from routers.admin_auth import admin_auth
from typing import Optional
from schemas import (BankAccountOutSchema, GameAccountOutSchema, ClientDetailOutSchema, ClientDetailOutSchema, 
                     ClientListResponseSchema, ToggleActiveStatusInSchema, VerifyBankInSchema, VerifyIdInSchema)
from django.utils import timezone
from datetime import datetime, timedelta, timezone

router = Router(tags=["後台-會員與KYC審核管理"], auth=admin_auth)

TW_TZ = timezone(timedelta(hours=8))

def serialize_client(c: Client) -> dict:
    return {
        "id": c.id,
        "account": c.account,
        "name": c.name,
        "id_code": c.id_code or "",
        "id_verified": c.id_verified,
        "phonenumber": c.phonenumber or "",
        "email": c.email or "",
        "registered_at": c.registered_at.astimezone(TW_TZ).strftime("%Y-%m-%d %H:%M:%S") if c.registered_at else "",
        "is_active": c.is_active,
        "is_tradable": c.is_tradable,
        "shop_payment": c.shop_payment,
        "virtual_account_payment": c.virtual_account_payment,
        "credit_card_payment": c.credit_card_payment,
        "idcard_front_img": c.idcard_front_img.url if c.idcard_front_img else None,
        "idcard_back_img": c.idcard_back_img.url if c.idcard_back_img else None,
        "bank_accounts": [
            {
                "id": b.id,
                "bank_name": b.bank_name,
                "account_number": b.account_number,
                "passbook_img": b.passbook_img.url if b.passbook_img else None,
                "account_holder_name": b.account_holder_name,
                "is_verified": b.is_verified,
                "created_at": b.created_at.astimezone(TW_TZ).strftime("%Y-%m-%d %H:%M:%S") if b.created_at else ""
            }
            for b in c.bank_accounts.all()
        ],
        "game_accounts": [
            {
                "id": g.id,
                "game_name": g.game_name,
                "game_id": g.game_id,
                "character_name": g.character_name
            }
            for g in c.game_accounts.all()
        ],
        "banned_records": c.banned_records or [],
        "unbanned_records": c.unbanned_records or []
    }

@router.get("/list", response=ClientListResponseSchema, summary="取得會員清單總表")
def list_clients(
    request,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    id_verified: Optional[bool] = None,
    is_tradable: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20
):
    qs = Client.objects.all().order_by('-id')

    if search:
        qs = qs.filter(account__icontains=search) | qs.filter(name__icontains=search) | qs.filter(id_code__icontains=search) | qs.filter(phonenumber__icontains=search) | qs.filter(email__icontains=search)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if id_verified is not None:
        qs = qs.filter(id_verified=id_verified)
    if is_tradable is not None:
        qs = qs.filter(is_tradable=is_tradable)

    total_count = qs.count()
    offset = (page - 1) * page_size
    clients_page = qs[offset:offset + page_size]

    items = [serialize_client(c) for c in clients_page]

    return {
        "status": "success",
        "items": items,
        "total_count": total_count
    }

@router.get("/{client_id}", response=ClientDetailOutSchema)
def get_member_detail(request, client_id: int):
    client = get_object_or_404(
        Client.objects.prefetch_related('bank_accounts', 'game_accounts'),
        id=client_id
    )
    return serialize_client(client)

@router.post("/{client_id}/verify-id", response=ClientDetailOutSchema)
def verify_client_id(request, client_id: int, payload: VerifyIdInSchema):
    client = get_object_or_404(Client, id=client_id)
    client.id_verified = payload.id_verified
    client.save()
    return serialize_client(client)

@router.post("/bank-accounts/{bank_account_id}/verify", response=ClientDetailOutSchema)
def verify_bank_account(request, bank_account_id: int, payload: VerifyBankInSchema):
    bank_acc = get_object_or_404(ClientBankAccount, id=bank_account_id)
    bank_acc.is_verified = payload.is_verified
    bank_acc.save()
    return serialize_client(bank_acc.client)

@router.put("/{client_id}/active-status", response=ClientDetailOutSchema)
def toggle_client_active_status(request, client_id: int, payload: ToggleActiveStatusInSchema):
    client = get_object_or_404(Client, id=client_id)
    operator = request.auth.username if hasattr(request.auth, 'username') else "admin"
    now_str = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = {
        "operator": operator,
        "timestamp": now_str,
        "reason": payload.reason
    }

    client.is_active = payload.is_active

    if not payload.is_active:
        # 禁用操作
        records = client.banned_records or []
        records.append(log_entry)
        client.banned_records = records
    else:
        # 解封/啟用操作
        records = client.unbanned_records or []
        records.append(log_entry)
        client.unbanned_records = records

    client.save()
    return serialize_client(client)

