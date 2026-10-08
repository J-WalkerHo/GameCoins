from ninja import Router, File, Form
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from decimal import Decimal
from tokens.models import Product, Client
from routers.admin_auth import admin_auth
from typing import Optional
from schemas import ProductOutSchema, ProductListResponseSchema, UpdateProductInSchema, CreateProductInSchema


admin_product_router = Router(tags=["後台-商品管理"], auth=admin_auth)

public_product_router = Router(tags=["前台-公開資料"])


@admin_product_router.get("/products", summary="取得產品清單總表")
def list_products(
    request, 
    trade_type: Optional[str]=None,
    game_type: Optional[str]=None,
    name: Optional[str]=None,
    is_active: Optional[bool]=None,
    is_soldout: Optional[bool]=None,
    page: int=1,
    page_size: int=20
        ):
    qs = Product.objects.all().order_by('-id')

    if trade_type:
        qs = qs.filter(trade_type=trade_type)
    if game_type:
        qs = qs.filter(game_type=game_type)

    if name:
        qs = qs.filter(name__icontains=name)

    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    if is_soldout is not None:
        qs = qs.filter(is_soldout=is_soldout)

    total_count = qs.count()
    offset = (page - 1) * page_size
    pages = qs[offset:offset + page_size]

    items = [
        {
            "id": product.id,
            "img_link": product.img_link,
            "name": product.name,   
            "trade_type": product.trade_type,
            "game_type": product.game_type,
            "ratio": float(product.ratio),
            "moq": float(product.moq),
            "max_oq": float(product.max_oq),
            "exclusive_client": product.exclusive_client.id if product.exclusive_client else None,
            # "single_digits_allowed": product.single_digits_allowed,
            "is_active": product.is_active,
            "is_soldout": product.is_soldout
        }
        for product in pages

    ]
    
    return{
        "status": "success",
        "total": total_count,
        "data": items
    }

@admin_product_router.post("/products")
def create_product(request, payload: CreateProductInSchema):
    if payload.exclusive_client:
        if not Client.objects.filter(id=payload.exclusive_client).exists():
            raise HttpError(400, f"找不到 ID 為 {payload.exclusive_client} 的會員")
    product = Product.objects.create(
        img_link=payload.img_link,
        name=payload.name,
        trade_type=payload.trade_type,
        game_type=payload.game_type,
        ratio=Decimal(payload.ratio),
        moq=Decimal(payload.moq),
        max_oq=Decimal(payload.max_oq),
        exclusive_client_id=payload.exclusive_client,
        single_digits_allowed=payload.single_digits_allowed,
        is_active=payload.is_active,
        is_soldout=payload.is_soldout
    )
    return {
        "status": "success",
        "message": f"商品{product.name}建立成功",   
    }

@admin_product_router.put("/products/{product_id}", summary="修改商品資訊")
def update_product(request, product_id: int, payload: UpdateProductInSchema):
    product = get_object_or_404(Product, id=product_id)

    if payload.img_link is not None: product.img_link = payload.img_link

    if payload.name is not None: product.name = payload.name

    if payload.trade_type is not None: product.trade_type = payload.trade_type

    if payload.game_type is not None: product.game_type = payload.game_type

    if payload.ratio is not None: product.ratio = Decimal(payload.ratio)

    if payload.moq is not None: product.moq = Decimal(payload.moq)

    if payload.max_oq is not None: product.max_oq = Decimal(payload.max_oq)

    if payload.exclusive_client is not None: 
        if not Client.objects.filter(id=payload.exclusive_client).exists():
            raise HttpError(400, f"找不到 ID 為 {payload.exclusive_client} 的會員")

        product.exclusive_client_id = payload.exclusive_client
    else:
        product.exclusive_client_id = None  # 如果 exclusive_client 為 None，將其設置為 NULL

    if payload.single_digits_allowed is not None: product.single_digits_allowed = payload.single_digits_allowed

    if payload.is_active is not None: product.is_active = payload.is_active

    if payload.is_soldout is not None: product.is_soldout = payload.is_soldout

    product.save()

    return {
        "status": "success",
        "message": f"商品{product.name}修改成功",   
    }

@admin_product_router.delete("/products/{product_id}")
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {
        "status": "success",
        "message": f"商品{product.name}刪除成功",   
    }

@public_product_router.get("/products", summary="取得產品清單總表")
def public_list_products(
    request, 
    trade_type: Optional[str]=None,
    game_type: Optional[str]=None,
        ):
    qs = Product.objects.all().order_by('-id')

    if trade_type:
        qs = qs.filter(trade_type=trade_type)
    if game_type:
        qs = qs.filter(game_type=game_type)

    qs = qs.filter(is_active=True)

    qs = qs.filter(is_soldout=False)

    total_count = qs.count()

    items = [
        {
            "id": product.id,
            "img_link": product.img_link,
            "name": product.name,   
            "trade_type": product.trade_type,
            "game_type": product.game_type,
            "ratio": float(product.ratio),
            "moq": float(product.moq),
            "max_oq": float(product.max_oq),
        }
        for product in qs

    ]
    
    return{
        "status": "success",
        "total": total_count,
        "data": items
    }
