from ninja import Router
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from typing import Optional, List
from decimal import Decimal
import random

from tokens.models import Order, Product
from accounts.models import Client

from schemas import CreateOrderInSchema, ClientProductOutSchema, ClientOrderDetailOutSchema, ClientOrderListResponseSchema

router = Router(tags=["前台會員-訂單交易"])

def generate_order_id() -> str:
    now_str = timezone.now().strftime("%Y%m%d%H%M%S")
    rand_str = f"{random.randint(1000, 9999)}"

    return f"ORD{now_str}{rand_str}"

def serialize_client_order(o: Order) -> dict:
    return {
        "id": o.id,
        "order_id": o.order_id,
        "product": {
            "id": o.product.id,
            "name": o.product.name
        } if o.product else None,
        "trade_type": o.trade_type,
        "order_status": o.order_status,
        "order_price": float(o.order_price),
        "game_coins": float(o.game_coins),
        "payment_info": o.payment_info or "",
        "payment_source": o.payment_source or "",
        "game_id": o.game_id,
        "game_account": o.game_account,
        "created_time": o.created_time.strftime("%Y-%m-%d %H:%M:%S") if o.created_time else "",
        "paid_time": o.paid_time.strftime("%Y-%m-%d %H:%M:%S") if o.paid_time else None,
        "transfered_time": o.transfered_time.strftime("%Y-%m-%d %H:%M:%S") if o.transfered_time else None,
    }

@router.post("/orders", response=ClientOrderDetailOutSchema)
def create_client_order(request, payload:CreateOrderInSchema):
    client = get_object_or_404(Client, id=payload.client_id)
    product = get_object_or_404(Product, id=payload.product_id)

    if hasattr(product, 'is_active') and not product.is_active:
        raise HttpError(400, "商品目前已下架，無法下單")

    if product.single_digits_allowed and payload.order_price % 10 !=0: 
        raise HttpError(400, "此產品不支援下單個位數金額，請重新輸入")
    
    min_qty = getattr(product, 'min_order_quantity', getattr(product, 'moq', 0))
    if payload.order_price < min_qty:
        raise HttpError(400, f"下單金額小於最小下單金額{min_qty}，請重新輸入")

    if product.max_oq and payload.order_price > product.max_oq:
        raise HttpError(400, f"下單金額大於最大下單金額{product.max_oq}，請重新輸入")

    buy_coins = payload.order_price * product.ratio
    total_price = payload.order_price

    if product.fee > 0:
        total_price += product.fee
    
    simulated_payment_info = f"繳費帳號/代碼: {random.randint(100000000000, 999999999999)}"

    order = Order.objects.create(
        order_id=generate_order_id(),
        client=client,
        product=product,
        trade_type=getattr(product, 'trade_type', getattr(product, 'type', 'sell')),
        order_status='pending',
        order_price=Decimal(str(total_price)),
        game_coins=Decimal(str(buy_coins)),
        payment_info=simulated_payment_info,
        payment_source=payload.payment_source,
        game_id=payload.game_id,
        game_account=payload.game_account
    )

    return serialize_client_order(order)

@router.get("/orders", response=ClientOrderListResponseSchema)
def list_client_orders(
    request,
    client_id: int,                      # 會員 ID
    order_status: Optional[str] = None,  # pending / paid / transfered / completed / cancelled / failed
    page: int = 1,
    page_size: int = 10
):
    qs = Order.objects.filter(client_id=client_id).select_related('product').order_by('-id')

    if order_status:
        qs = qs.filter(order_status=order_status)

    total_count = qs.count()
    offset = (page - 1) * page_size
    orders_page = qs[offset:offset + page_size]

    items = [serialize_client_order(o) for o in orders_page]
    return {"items": items, "total_count": total_count}

@router.get("/orders/{order_db_id}", response=ClientOrderDetailOutSchema)
def get_client_order_detail(request, order_db_id: int, client_id: int):
    order = get_object_or_404(
        Order.objects.select_related('product'),
        id=order_db_id,
        client_id=client_id  # 確保只能查自己的訂單
    )
    return serialize_client_order(order)