from rest_framework.serializers import ModelSerializer
from .models import Dish, Menu, Menu_Dish, Order, Rate, Shop, User,UserType,Comment
import cloudinary.uploader

class UserSerializer(ModelSerializer):
    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(data['password'])
        file = cloudinary.uploader.upload(validated_data['avatar'])
        user.avatar = file['secure_url']
        user.is_active=1
        user.save()

        return user

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs={
            'password': {
                'write_only': True
            },
            'is_superuser': {
                'read_only': True
            },
            'date_joined': {
                'read_only': True
            },
            'groups': {
                'read_only': True
            },
            'user_permissions': {
                'read_only': True
            },
            'last_login': {
                'read_only': True
            }
        }

class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields='__all__'

class DishSerializer(ModelSerializer):
    def create(self, validated_data):
        dish = Dish(**validated_data)
        shop_id = validated_data.get('shop_id')
        if shop_id:
            dish.shop = Shop.objects.get(user_id=shop_id)

        dish.save()
        return dish

    class Meta:
        model = Dish
        fields='__all__'

class MenuSerializer(ModelSerializer):
    class Meta:
        model = Menu
        fields='__all__'

class MenuDishSerializer(ModelSerializer):
    class Meta:
        model = Menu_Dish
        fields='__all__'

class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields='__all__'

class CommentSerializer(ModelSerializer):
    def create(self, validated_data):
        comment = super().create(validated_data)
        comment.dish = validated_data['dish_id']
        comment.shop = validated_data['shop_id']
        comment.parent = validated_data['parent_id']
        return comment
    class Meta:
        model = Comment
        fields='__all__'
        extra_kwargs={
            'user_id': {
                'read_only':True
            }
        }

class RateSerializer(ModelSerializer):
    def create(self, validated_data):
        rate = super().create(validated_data)
        rate.dish_id_id = validated_data['dish_id']
        return rate

    class Meta:
        model = Rate
        fields = '__all__'