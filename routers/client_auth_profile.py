import os
from uuid import uuid4
from ninja import Router, File, Form
from ninja.errors import HttpError
from ninja.files import UploadedFile
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from accounts.models import Client, ClientBankAccount, ClientGameAccount
from typing import Optional
from schemas import ClientRegisterInSchema, AddGameAccountInSchema, AddBankAccountInSchema


public_client_router = Router(tags=["前台-會員註冊與資料管理"])

client_profile_router = Router(tags=["前台會員-個人資料管理"])

@public_client_router.post("/register", summary="會員註冊")
def register_client(request, payload: ClientRegisterInSchema):
    if Client.objects.filter(account=payload.account).exists():
        raise HttpError(400, "帳號已存在")
    if Client.objects.filter(phonenumber=payload.phonenumber).exists():
        raise HttpError(400, "手機號碼已存在")
    if Client.objects.filter(email=payload.email).exists():
        raise HttpError(400, "電子郵件已存在")
    if Client.objects.filter(id_code=payload.id_code).exists():
        raise HttpError(400, "身分證字號已存在")

    client = Client.objects.create(
        account=payload.account,
        password=make_password(payload.password),
        name=payload.name,
        id_code=payload.id_code,
        phonenumber=payload.phonenumber,
        email=payload.email,
            )

    return {"message": "註冊成功", "client_id": client.id, "account": client.account}

@client_profile_router.post("/upload-idcard", summary="上傳身分證照片")
def upload_idcard(request, 
                  client_id: int,
                  idcard_front: Optional[UploadedFile] = File(None),
                  idcard_back: Optional[UploadedFile] = File(None)
                  ):
    
    user = request.auth  # 假設使用者已經登入，並且 auth 中包含使用者資訊
    if not isinstance(user, Client):
        raise HttpError(403, "未授權的操作")

    client = get_object_or_404(Client, id=client_id)
    upload_dir = os.path.join("media", "idcard")
    os.makedirs(upload_dir, exist_ok=True)

    # 儲存前面照片
    if idcard_front:
        ext = idcard_front.name.split('.')[-1]
        fname = f"front_{uuid4().hex}.{ext}"
        fpath = os.path.join(upload_dir, fname)
        with open(fpath, "wb+") as dst:
            for chunk in idcard_front.chunks():
                dst.write(chunk)
        client.idcard_front_img = f"idcard/{fname}"

    # 儲存後面照片
    if idcard_back:
        ext = idcard_back.name.split('.')[-1]
        fname = f"back_{uuid4().hex}.{ext}"
        fpath = os.path.join(upload_dir, fname)
        with open(fpath, "wb+") as dst:
            for chunk in idcard_back.chunks():
                dst.write(chunk)
        client.idcard_back_img = f"idcard/{fname}"


    client.save()
    return {"message": "身分證照片上傳成功"}

@client_profile_router.post("/game-accounts")
def add_game_account(request, client_id: int, payload: AddGameAccountInSchema):
    client = get_object_or_404(Client, id=client_id)
    game_acc = ClientGameAccount.objects.create(
        client=client,
        game_name=payload.game_name,
        game_id=payload.game_id,
        character_name=payload.character_name
    )
    return {
        "id": game_acc.id,
        "game_name": game_acc.game_name,
        "game_id": game_acc.game_id,
        "character_name": game_acc.character_name
    }

@client_profile_router.post("/bank-accounts")
def add_bank_account(
    request,
    client_id: int,
    bank_name: str = Form(...),
    account_number: str = Form(...),
    account_holder_name: str = Form(...),
    passbook_img: Optional[UploadedFile] = File(None)
):
    client = get_object_or_404(Client, id=client_id)
    passbook_path = None

    if passbook_img:
        upload_dir = os.path.join("media", "passbook")
        os.makedirs(upload_dir, exist_ok=True)
        ext = passbook_img.name.split('.')[-1]
        fname = f"passbook_{uuid4().hex}.{ext}"
        fpath = os.path.join(upload_dir, fname)
        with open(fpath, "wb+") as dst:
            for chunk in passbook_img.chunks():
                dst.write(chunk)
        passbook_path = f"passbook/{fname}"

    bank_acc = ClientBankAccount.objects.create(
        client=client,
        bank_name=bank_name,
        account_number=account_number,
        account_holder_name=account_holder_name,
        passbook_img=passbook_path,
    )

    return {
        "id": bank_acc.id,
        "bank_name": bank_acc.bank_name,
        "account_number": bank_acc.account_number,
        "account_holder_name": bank_acc.account_holder_name,
        "is_verified": bank_acc.is_verified
    }