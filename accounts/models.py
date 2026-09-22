from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomAdminUser(BaseUserManager):
    is_super_admin = models.BooleanField(default=False, verbose_name="是否為超級管理員")
    is_active = models.BooleanField(default=True, verbose_name="是否啟用")

    permissions = models.JSONField(default=dict, blank=True, verbose_name="權限設定")

    class Meta:
        verbose_name = "管理員帳號"
        verbose_name_plural = verbose_name

class Client(models.Model):
    account = models.CharField(max_length=50, unique=True, verbose_name="帳號")
    password = models.CharField(max_length=128, verbose_name="密碼")
    name = models.CharField(max_length=50, verbose_name="會員名稱")
    id_code = models.CharField(max_length=10, unique=True, verbose_name="身分證字號")
    id_verified = models.BooleanField(default=True, verbose_name="身分證是否驗證完成")
    phonenumber = models.CharField(max_length=15, unique=True, verbose_name="手機號碼")
    email = models.EmailField(unique=True, verbose_name="電子郵件")
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="註冊時間")
    is_active = models.BooleanField(default=True, verbose_name="是否啟用")
    is_tradable = models.BooleanField(default=True, verbose_name="是否可交易")

    idcard_front_img = models.ImageField(upload_to='idcard_front/', null=True, blank=True, verbose_name="身分證正面照片")
    idcard_back_img = models.ImageField(upload_to='idcard_back/', null=True, blank=True, verbose_name="身分證背面照片")

    shop_payment = models.BooleanField(default=True, verbose_name="可否超商支付")
    virtual_account_payment = models.BooleanField(default=True, verbose_name="可否虛擬帳號支付")
    credit_card_payment = models.BooleanField(default=True, verbose_name="可否信用卡支付")

    banned_records = models.JSONField(default=list, blank=True, verbose_name="帳號禁用紀錄")
    unbanned_records = models.JSONField(default=list, blank=True, verbose_name="帳號啟用紀錄")

    def __str__(self):
        return f"{self.account} {self.name}"

class ClientBankAccount(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bank_accounts', verbose_name="會員")
    bank_name = models.CharField(max_length=100, verbose_name="銀行名稱")
    account_number = models.CharField(max_length=20, verbose_name="銀行帳號")
    passbook_img = models.ImageField(upload_to='passbook/', null=True, blank=True, verbose_name="存摺封面照片")
    account_holder_name = models.CharField(max_length=100, verbose_name="帳戶持有人姓名")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    is_verified = models.BooleanField(default=False, verbose_name="是否已驗證")

class ClientGameAccount(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='game_accounts', verbose_name="會員")
    game_name = models.CharField(max_length=100, verbose_name="遊戲名稱")
    game_id = models.CharField(max_length=100, verbose_name="遊戲帳號ID")
    character_name = models.CharField(max_length=100, verbose_name="角色名稱")

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, verbose_name="網站名稱")
    is_notice_enabled = models.BooleanField(default=True, verbose_name="是否啟用網站公告")
    notice = models.TextField(blank=True, verbose_name="網站公告(跑馬燈)")
    pc_logo_img = models.ImageField(upload_to='site_logo/', null=True, blank=True, verbose_name="電腦版Logo")
    mobile_logo_img = models.ImageField(upload_to='site_logo/', null=True, blank=True, verbose_name="手機版Logo")
    address_logo_img = models.ImageField(upload_to='site_logo/', null=True, blank=True, verbose_name="網址Logo")
    company_name = models.CharField(max_length=100, blank=True, verbose_name="公司名稱")
    company_id = models.CharField(max_length=100, blank=True, verbose_name="公司統編")
    company_phone = models.CharField(max_length=200, blank=True, verbose_name="公司電話")
    company_mail = models.CharField(max_length=200, blank=True, verbose_name="公司信箱")
    company_line = models.CharField(max_length=200, blank=True, verbose_name="公司Line")
    css_option = models.CharField(max_length=50, default="default", verbose_name="版面主題風格")

    last_editor = models.CharField(max_length=50, blank=True, null=True, verbose_name="最後編輯管理者")
    last_edited_time = models.DateTimeField(auto_now=True, verbose_name="最後編輯時間")

class CashFlowSettings(models.Model):
    ENVIRONMENT_CHOICES = [('test', '測試環境'), ('prod', '正式環境')]

    type = models.CharField(max_length=10, choices=ENVIRONMENT_CHOICES, default='test')
    cashflow_supplier = models.CharField(max_length=50, verbose_name="金流廠商名稱(如:綠界/藍新)")
    merchant_id = models.CharField(max_length=100, verbose_name="商店代號 MerchantID")
    hash_key = models.CharField(max_length=100)
    hash_iv = models.CharField(max_length=100)

    shop_payment = models.BooleanField(default=True, verbose_name="開啟超商支付")
    virtual_payment = models.BooleanField(default=True, verbose_name="開啟虛擬帳號")
    creditcard_payment = models.BooleanField(default=True, verbose_name="開啟信用卡")

    # 服務費與手續費設定
    withdrawal_status = models.BooleanField(default=False, verbose_name="是否有出款服務費")
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="服務費定額")
    fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="服務費比率(%)")
    max_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    withdrawal_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="出款服務費定額")
    withdrawal_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="出款服務費比率(%)")

class Banner(models.Model):
    pc_banner_img = models.CharField(max_length=255, verbose_name="PC Banner 圖址")
    mobile_banner_img = models.CharField(max_length=255, verbose_name="手機 Banner 圖址")
    banner_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="點擊連結")

class Picture(models.Model):
    filename = models.CharField(max_length=100)
    file_link = models.CharField(max_length=255, verbose_name="圖片來源網址")
    type = models.CharField(max_length=50, verbose_name="圖片分類")