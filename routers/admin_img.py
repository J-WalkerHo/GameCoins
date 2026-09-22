import os
from uuid import uuid4
from ninja import Router, File, Form
from ninja.files import UploadedFile
from typing import List, Optional
from django.shortcuts import get_object_or_404
from accounts.models import Picture
from routers.admin_auth import admin_auth
from schemas import UploadImageOutSchema, PictureItemOutSchema, PictureListResponseSchema

router = Router(tags=["後台-圖片管理"], auth=admin_auth)

@router.post("/pictures/upload", response=UploadImageOutSchema, auth=admin_auth)
def upload_picture(
    request, 
    file: UploadedFile = File(...),
    type: str = Form("logo")
):

    ext = file.name.split('.')[-1]
    new_filename = f"{uuid4()}.{ext}"
    upload_dir = os.path.join("media", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, new_filename)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    file_link = f"/media/uploads/{new_filename}"

    picture = Picture.objects.create(
        filename=new_filename,
        file_link=file_link,
        type=type
    )

    return {
        "id": picture.id,
        "filename": picture.filename,
        "file_link": picture.file_link,
        "type": picture.type
    }

@router.delete("/pictures/{picture_id}")
def delete_picture(request, picture_id: int):
    picture = get_object_or_404(Picture, id=picture_id)
    picture.delete()  # 刪除 DB 紀錄
    return {"message": f"圖片 {picture.filename} 已成功刪除"}

@router.get("/pictures", response=PictureListResponseSchema, auth=admin_auth)
def list_pictures(
    request, 
    type: Optional[str] = None,
    search: Optional[str] = None
    ):
    qs = Picture.objects.all().order_by('-id')

    if type:
        qs=qs.filter(type=type)

    if search:
        qs = qs.filter(filename__icontains=search)

    total_count = qs.count()

    items = [
        {
            "id": pic.id,
            "filename": pic.filename,
            "file_link": pic.file_link,
            "type": pic.type

        } for pic in qs
    ]

    return {
        "items": items,
        "total_count": total_count  
    }   
