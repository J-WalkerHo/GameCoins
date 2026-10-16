from ninja import Router
from ninja.errors import HttpError
from typing import Optional
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal

from tokens.models import Order
from routers.admin_auth import admin_auth
from schemas import OrderOutSchema, ProductOutSchema, OrderDetailOutSchema, UpdateOrderStatusInSchema

router = Router(tags=["後台-交易訂單管理"], auth=admin_auth)

def serialize_order(o: Order) -> dict:
    return{
        "id": o.id,
        "order_id": o.order_id,
        "client": {
            "id": o.client.id,
            "account": o.client.account,
            "name": o.client.name,
            "phonenumber": getattr(o.client, 'phonenumber', '') or ""
        },
    "product": {
            "id": o.product.id,
            "name": o.product.name,
        } if o.product else None,
        "trade_type": o.trade_type,
        "order_status": o.order_status,
        "order_price": float(o.order_price),
        "game_coins": float(o.game_coins),
        "payment_info": o.payment_info or "",
        "payment_source": o.payment_source or "",
        "game_id": o.game_id,
        "game_account": o.game_account,
        "admin_note": getattr(o, 'admin_note', '') or "",
        "status_logs": getattr(o, 'status_logs', []) or [],
        "created_time": o.created_time.strftime("%Y-%m-%d %H:%M:%S") if o.created_time else "",
        "paid_time": o.paid_time.strftime("%Y-%m-%d %H:%M:%S") if o.paid_time else None,
        "transfered_time": o.transfered_time.strftime("%Y-%m-%d %H:%M:%S") if o.transfered_time else None,
        "completed_time": o.completed_time.strftime("%Y-%m-%d %H:%M:%S") if getattr(o, 'completed_time', None) else None,
    }

@router.get("/orders", summary="取得交易訂單清單")
def list_orders(
    request,
    order_status: Optional[str] = None,  # pending / paid / transfered / completed / cancelled / failed
    trade_type: Optional[str] = None,    # sell / buy
    search: Optional[str] = None,        # 搜尋: 訂單號 / 玩家名稱 / 帳號 / 角色 ID
    page: int = 1,
    page_size: int = 20
):

    qs = Order.objects.select_related('client', 'product').all().order_by('-id')

    if order_status:
        qs = qs.filter(order_status=order_status)

    if trade_type:
        qs = qs.filter(trade_type=trade_type)

    if search:
        qs = qs.filter(
            order_id__icontains=search
        ) | qs.filter(
            client__name__icontains=search
        ) | qs.filter(
            client__account__icontains=search
        ) | qs.filter(
            game_account__icontains=search
        )

    total_count = qs.count()
    offset = (page - 1) * page_size
    orders_page = qs[offset:offset + page_size]


@router.get("/orders/{order_id}", response=OrderDetailOutSchema, summary="取得單筆交易訂單詳細資訊")
def get_order_detail(request, order_id: str):
    order = get_object_or_404(Order.objects.select_related('client', 'product'), order_id=order_id)

    return serialize_order(order)

@router.put("/orders/{order_id}/status", response=OrderDetailOutSchema, summary="更新交易訂單狀態")
def update_order_status(request, order_id: str, payload: UpdateOrderStatusInSchema):
    order = get_object_or_404(Order.objects.select_related('client', 'product'), order_id=order_id)

    valid_statuses = ['pending', 'paid', 'transfered', 'cancelled', 'failed']

    if payload.order.status not in valid_statuses:
        raise HttpError(400, f"無效的訂單狀態: {payload.order.status}. 有效狀態為: {', '.join(valid_statuses)}")

    old_status = order.order_status
    new_status = payload.order.status
    now = timezone.now()

    if new_status == "paid" and not order.paid_time:
        order.paid_time = now

    elif new_status == "transfered" and not order.transfered_time:
        if not order.transfered_time:
            order.transfered_time = now

        if not order.paid_time:
            order.paid_time = now

    
        
 
    order.order_status = new_status
    order.save()
    return serialize_order(order)
