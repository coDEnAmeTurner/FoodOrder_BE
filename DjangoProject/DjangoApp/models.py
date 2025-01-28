from django.db import models
import django.db.models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField 

# Create your models here.
class UserType(models.TextChoices):
    QUANTRI = 'QUANTRI'
    CANHAN = 'CANHAN'
    CUAHANG = 'CUAHANG'

class PurchaseType(models.TextChoices):
    TRUCTUYEN = 'TRUCTUYEN'
    TIENMAT = 'TIENMAT'

class Buoi(models.TextChoices):
    SANG = 'SANG'
    CHIEU = 'CHIEU'

class User(AbstractUser) :
    avatar = CloudinaryField('avatar',null=True)
    ten = models.CharField(blank=False,null=False,max_length=200)
    email = models.TextField(blank=True,null=True)
    sdt = models.CharField(blank=True,null=True,max_length=11)
    type = models.CharField(max_length=7,choices=UserType.choices,default=UserType.CANHAN)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    
class Order(models.Model):
    shop_id = models.ForeignKey('Shop',on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=0)
    loai_thanh_toan = models.CharField(max_length=10,choices=PurchaseType.choices,default=PurchaseType.TIENMAT)
    ngay_order = models.DateField(auto_now_add=True)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Dish(models.Model):
    shop_id = models.ForeignKey('Shop',on_delete=models.CASCADE)
    ten = models.CharField(blank=False,null=False,max_length=200)
    tien_thuc_an = models.FloatField(blank=False,null=False,default=0)
    is_available = models.BooleanField(default=True,blank=True,null=True)
    buoi = models.CharField(max_length=7,choices=Buoi.choices,blank=True,null=True)
    chu_thich = models.TextField(blank=True,null=True)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Order_Dish(models.Model):
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE)
    dish_id = models.ForeignKey('Dish',on_delete=models.CASCADE)
    so_luong = models.IntegerField(default=1,blank=False,null=False)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('order_id','dish_id')

class Shop(models.Model):
    dia_diem = models.TextField(blank=True,null=False)
    is_valid = models.BooleanField(default=0,blank=False,null=False)
    tien_van_chuyen = models.FloatField(default=0,blank=False,null=False)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Menu(models.Model):
    shop_id = models.ForeignKey('Shop',on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Menu_Dish(models.Model):
    menu_id = models.ForeignKey('Menu', on_delete=models.CASCADE)
    dish_id = models.ForeignKey('Dish',on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    class Meta:
        unique_together = ('menu_id','dish_id')
