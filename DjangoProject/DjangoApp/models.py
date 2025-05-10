from django.db import models
import django.db.models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField 

# Create your models here.
class UserType(models.TextChoices):
    NONE = 'NONE'
    INDIVIDUAL = 'INDIVIDUAL'
    SHOP = 'SHOP'

class PurchaseType(models.TextChoices):
    BANKING = 'BANKING'
    CASH = 'CASH'

class DaySession(models.TextChoices):
    MORNING = 'MORNING'
    AFTERNOON = 'AFTERNOON'

class User(AbstractUser) :
    avatar = CloudinaryField('avatar',null=True)
    name = models.CharField(blank=False,null=False,max_length=200)
    email = models.TextField(blank=True,null=True)
    phone = models.CharField(blank=True,null=True,max_length=11)
    type = models.CharField(max_length=10,choices=UserType.choices,default=UserType.INDIVIDUAL)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    
class Order(models.Model):
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True,blank=False)
    is_valid = models.BooleanField(default=0)
    payment_type = models.CharField(max_length=10,choices=PurchaseType.choices,default=PurchaseType.CASH)
    date_order = models.DateField(auto_now_add=True)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Dish(models.Model):
    shop = models.ForeignKey('Shop',on_delete=models.CASCADE,to_field='user_id',null=True,blank=False)
    name = models.CharField(blank=False,null=False,max_length=200)
    price = models.FloatField(blank=False,null=False,default=0)
    is_available = models.BooleanField(default=True,blank=True,null=True)
    day_session = models.CharField(max_length=10,choices=DaySession.choices,blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Order_Dish(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    dish = models.ForeignKey('Dish',on_delete=models.CASCADE)
    count = models.IntegerField(default=0,blank=False,null=False)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('order','dish')

class Shop(models.Model):
    user = models.OneToOneField('user',on_delete=models.CASCADE,default=1,primary_key=True)
    location = models.TextField(blank=True,null=False)
    is_valid = models.BooleanField(default=0,blank=False,null=False)
    ship_payment = models.FloatField(default=0,blank=False,null=False)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Menu(models.Model):
    name = models.CharField(blank=False,null=False,default='Thực Đơn',max_length=350)
    shop = models.ForeignKey('Shop',on_delete=models.CASCADE,to_field='user',null=True,blank=False)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Menu_Dish(models.Model):
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='menu_dish_pairs')
    dish = models.ForeignKey('Dish',on_delete=models.CASCADE)
    count = models.IntegerField(default=1,blank=False,null=False)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    class Meta:
        unique_together = ('menu','dish')

class Comment(models.Model):
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True,blank=False)
    shop = models.ForeignKey('Shop',on_delete=models.CASCADE,null=True,blank=False,to_field='user')
    dish = models.ForeignKey('Dish',on_delete=models.CASCADE,null=True,blank=False)
    parent = models.ForeignKey('Comment',on_delete=models.CASCADE,null=True,blank=False)
    content = models.TextField(blank=True,null=True)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Rate(models.Model):
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True,blank=False)
    dish = models.ForeignKey('Dish',on_delete=models.CASCADE,null=True,blank=False)
    stars = models.IntegerField(default=1,blank=False,null=False)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    class Meta:
        unique_together = ('user','dish')
