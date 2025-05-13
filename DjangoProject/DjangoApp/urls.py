from rest_framework import routers
from django.urls import path, include
from DjangoApp import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('dishs', views.DishViewSet)
router.register('menus', views.MenuViewSet)
router.register('comments', views.CommentViewSet)
router.register('orders', views.OrderViewSet)

urlpatterns = [
    path('',include(router.urls))
]