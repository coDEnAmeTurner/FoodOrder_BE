from rest_framework import routers
from django.urls import path, include
from DjangoApp import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)

urlpatterns = [
    path('',include(router.urls))
]