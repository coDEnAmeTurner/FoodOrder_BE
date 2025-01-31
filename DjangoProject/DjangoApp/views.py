from rest_framework import viewsets,permissions,parsers,status
from rest_framework.viewsets import generics
from rest_framework.response import Response
from DjangoApp.serializers import UserSerializer
from .models import Shop, User,UserType
from rest_framework.decorators import action


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    parser_classes = [parsers.MultiPartParser]
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action.__eq__('current_user'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get'],detail=False,url_path='current-user')
    def current_user(self, request):
        serializer = UserSerializer(request.user)
        return Response(data=serializer.data,status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user=User.objects.get(pk=int(response.data['id']))

        if user.type.__eq__(UserType.CUAHANG.__str__()):
            shop = Shop()
            shop.user = user
            shop.dia_diem = request.data['dia_diem']
            shop.tien_van_chuyen = float(request.data['tien_van_chuyen'])
            shop.save()

        return response
    



    
    
    

