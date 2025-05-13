from rest_framework import permissions
from .models import Shop, UserType

class SuperUserPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser == 1

class ShopPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and ((request.user.type.__eq__(UserType.SHOP.__str__()) and Shop.objects.get(pk=request.user.id).is_valid == 1) or request.user.is_superuser)