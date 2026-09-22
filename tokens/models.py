from django.db import models
from accounts.models import Client
from django.core.validators import MinValueValidator

# --- 1. 產品列表 (Products) ---
class Product(models.Model):
    TRADE_TYPE_CHOICES = [
        ('sell', '出售(平台賣給玩家)'),
        ('buy', '收購(平台向玩家買)'),
    ]

    img_link = models.CharField(max_length=255, verbose_name="商品圖片來源")
    name = models.CharField(max_length=100, verbose_name="商品名稱(如: 新楓之檎幣)")
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPE_CHOICES, default='sell', verbose_name="交易類型")
    
    # 1 台幣 = 多少遊戲幣，例如 比值 1000 表示 1 TWD = 1000 遊戲幣
    ratio = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="兌換比值")
    
    is_active = models.BooleanField(default=True, verbose_name="是否上架")
    is_exclusive = models.BooleanField(default=False, verbose_name="是否專屬商品")
    exclusive_client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="指定專屬會員")
    is_soldout = models.BooleanField(default=False, verbose_name="是否售完")
    
    single_digits_allowed = models.BooleanField(default=False, verbose_name="是否可下單個位數金額")
    moq = models.DecimalField(max_digits=10, decimal_places=2, default=100, verbose_name="最小下單金額(MOQ)")
    max_oq = models.DecimalField(max_digits=10, decimal_places=2, default=10000, verbose_name="最大下單金額(MaxOQ)")

    def __str__(self):
        return f"[{self.get_trade_type_display()}] {self.name}"


# --- 2. 訂單列表 (Order List) ---
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待繳費'),
        ('paid', '已繳費/交易中'),
        ('transfered', '已移轉/已交貨'),
        ('completed', '交易完成'),
        ('cancelled', '已取消'),
        ('failed', '交易失敗/退款'),
    ]

    order_id = models.CharField(max_length=50, unique=True, verbose_name="訂單編號")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="關聯會員")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="購買商品")
    
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="訂單狀態")
    order_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="訂單金額(TWD)")
    game_coins = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="對應遊戲幣數量")
    
    # 金流與繳費資訊
    payment_info = models.TextField(blank=True, null=True, verbose_name="繳費資訊(如虛擬帳號/超商條碼)")
    payment_source = models.CharField(max_length=50, blank=True, null=True, verbose_name="繳費管道(信用卡/超商/WebATM/LINE)")
    
    # 玩家遊戲角色的快照資訊
    game_id = models.CharField(max_length=50, verbose_name="伺服器/遊戲名稱")
    game_account = models.CharField(max_length=50, verbose_name="玩家遊戲角色ID")

    created_time = models.DateTimeField(auto_now_add=True, verbose_name="訂單建立時間")
    paid_time = models.DateTimeField(null=True, blank=True, verbose_name="繳費時間")
    transfered_time = models.DateTimeField(null=True, blank=True, verbose_name="移轉/交貨時間")

    def __str__(self):
        return f"訂單 {self.order_id} - {self.client.name}"