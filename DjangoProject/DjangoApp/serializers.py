from rest_framework.serializers import ModelSerializer
from .models import Shop, User,UserType
import cloudinary.uploader

class UserSerializer(ModelSerializer):
    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(data['password'])
        file = cloudinary.uploader.upload(validated_data['avatar'])
        user.avatar = file['secure_url']
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
