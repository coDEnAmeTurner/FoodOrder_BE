from rest_framework import viewsets,permissions,parsers,status
from rest_framework.viewsets import generics
from rest_framework.response import Response
from .serializers import *
from .pagination import DishPaginator
from .models import *
from rest_framework.decorators import action
from .perms import ShopPermissions, SuperUserPermissions

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    parser_classes = [parsers.MultiPartParser]
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action.__eq__('current_user'):
            return [permissions.IsAuthenticated()]
        if self.action.__eq__('verify_shop'):
            return [SuperUserPermissions()]
        return [permissions.AllowAny()]

    @action(methods=['get'],detail=False,url_path='current-user')
    def current_user(self, request):
        serializer = UserSerializer(request.user)
        return Response(data=serializer.data,status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if self.request.user.type.__eq__(UserType.CUAHANG.__str__()):
            shop = Shop()
            shop.user_id = self.request.user
            shop.dia_diem = request.data['dia_diem']
            shop.tien_van_chuyen = float(request.data['tien_van_chuyen'])
            shop.save()

        return response
    
    @action(methods=['patch'],detail=True,url_path='verify-shop')
    def verify_shop(selft, request, pk):
        shop = Shop.objects.get(user_id=pk)
        shop.is_valid = True
        shop.save()
        user = User.objects.get(pk=pk)

        return Response(data={**UserSerializer(user).data,**ShopSerializer(shop).data},status=status.HTTP_200_OK)

class DishViewSet(viewsets.ViewSet,generics.UpdateAPIView, generics.CreateAPIView,generics.ListAPIView):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [ShopPermissions]
    pagination_class = DishPaginator

    def get_permissions(self):
        if self.action.__eq__('list'):
            return [permissions.IsAuthenticated()]

        return super().get_permissions()

    def get_queryset(self):
        shop_id = self.request.GET.get('shop_id')
        name = self.request.GET.get('name')
        from_price = self.request.GET.get('from_price')
        to_price = self.request.GET.get('to_price')
        is_available = self.request.GET.get('is_available')
        day_session = self.request.GET.get('day_session')
        queries = self.queryset

        if shop_id:
            queries = queries.filter(shop_id=shop_id)
        if name:
            queries = queries.filter(name__icontains=name)
        if from_price or to_price:
            queries = queries.filter(price__gt=float(from_price), price__lt=float(to_price))
        if is_available:
            queries = queries.filter(is_available=bool(is_available))
        if day_session:
            queries = queries.filter(day_session__icontains=day_session)
        return queries

class MenuViewSet(viewsets.ViewSet,generics.UpdateAPIView, generics.CreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [ShopPermissions]

    def add_dishs_core(self, request, menu):
        # request.data has a key 'dish'
        # 'dish': [
        #    {"id": 1, "count": 2},
        #    {"id": 2, "count": 2},
        #  ]
        dish_list = request.data['dish']
        for jobj in dish_list:
            menu_dish = Menu_Dish()
            menu_dish.menu = menu
            menu_dish.dish = Dish.objects.get(pk=jobj['id'])
            menu_dish.count = jobj['count']
            menu_dish.save()

    def create(self, request, *args, **kwargs):
        try:
            menu_response = super().create(request, *args, **kwargs)
            menu = Menu.objects.get(pk=int(menu_response.data['id']))
            shop = Shop.objects.filter(user_id=self.request.user.id).first()
            if shop:
                menu.shop = shop
            menu.save()
            
            self.add_dishs_core(request, menu)

            return Response(data=MenuSerializer(menu).data,status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={"error_msg":f"{str(e)}", "param_id":kwargs.get("pk")},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            menu_id = response.data['id']
            menu = Menu.objects.get(pk=int(menu_id))
            Menu_Dish.objects.delete(menu_id=int(menu.id))
            self.add_dishs_core(request, menu)
            return response
        except Menu.DoesNotExist:
            return Response(data={"error_msg":f"Menu {kwargs.get("pk")} not found."},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"error_msg":f"{e.__str__()}","param_id":kwargs.get("pk")},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(methods=['post'],detail=True,url_path='dishs')
    def add_dish(self, request, pk):
        try:
            menu = Menu.objects.get(pk=pk)
            self.add_dishs_core(request, menu)

            return Response(data=MenuSerializer(menu).data,status=status.HTTP_201_CREATED)
        except Menu.DoesNotExist:
            return Response(data={"error_msg":"Menu not found."},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"error_msg":f"{str(e)}","param_id":pk},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class OrderViewSet(viewsets.ViewSet,generics.UpdateAPIView,  generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action.__eq__('verify'):
            return [ShopPermissions()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        # request.data will have both keys: dish or menu
        # {
        #   payment_type: 'CASH'
        #   dish: [
        #    {'id':1,'count':2},
        #    {'id':2,'count':3},
        #   ],
        #   menu: [1,2,3,4,5,...]
        #}

        try:
            response = super().create(request, *args, **kwargs)
            user = self.request.user
            order = Order.objects.get(pk=int(response.data['id']))
            order.user = user
            order.payment_type = response.data['payment_type']
            order.save();

            dish_list = request.data['dish']
            menu_id_list = request.data['menu']

            if dish_list or menu_id_list:
            #   dish: [
            #    {'id':1,'count':2},
            #    {'id':2,'count':3},
            #   ],
                if dish_list:
                    for jobj in dish_list:
                        try:
                            order_dish = Order_Dish()
                            dish = Dish.objects.get(pk=jobj['id'])
                            count = jobj['count']
                            order_dish.order = order
                            order_dish.dish = dish
                            order_dish.count += count
                            order_dish.save()
                        except Dish.DoesNotExist as od:
                            return Response(data={"error_msg":f"Dish {jobj['id']} not found."},status=status.HTTP_404_NOT_FOUND)
                        except Exception as od:
                            return Response(data={"error_msg":f"{str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            #   menu: [1,2,3,4,5,...]
                if menu_id_list:
                    for id in menu_id_list:
                        try:
                            menu = Menu.objects.get(pk=id)
                            md_pairs = menu.menu_dish_pairs.all()
                            for pair in md_pairs:
                                order_found = Order_Dish.objects.filter(order=order,dish=pair.dish).first()
                                if (order_found):
                                    order_found.count += pair.count
                                    order_found.save()
                                else:
                                    order_dish = Order_Dish()
                                    order_dish.order = order
                                    order_dish.dish = pair.dish
                                    order_dish.count += pair.count 
                                    order_dish.save()
                        except Menu.DoesNotExist as od:
                            return Response(data={"error_msg":f"Menu {id} not found."},status=status.HTTP_404_NOT_FOUND)
                        except Exception as od:
                            return Response(data={"error_msg":f"{str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(data=OrderSerializer(order).data,status=status.HTTP_201_CREATED)
        except Order.DoesNotExist as od:
            return Response(data={"error_msg":f"Order {response.data['id']} not found."},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"error_msg":f"{str(e)}","param_id":kwargs.get("pk")},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(methods=['patch'],detail=True,url_path='verify')
    def verify(selft, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            order.is_valid = True
            order.save()

            return Response(data=OrderSerializer(order).data,status=status.HTTP_200_OK)
        except Order.DoesNotExist as od:
            return Response(data={"error_msg":f"Order {pk} not found."},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"error_msg":f"{str(e)}","param_id":pk},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentViewSet(viewsets.ViewSet,generics.UpdateAPIView, generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            comment = Comment.objects.get(pk=int(response.data['id']))
            comment.user_id = self.request.user
            comment.save()
            return Response(data=CommentSerializer(comment).data,status=status.HTTP_201_CREATED)
        except Comment.DoesNotExist as od:
            return Response(data={"error_msg":f"Comment {response.data['id']} not found."},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"error_msg":f"{str(e)}","param_id":kwargs.get("pk")},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class RateViewSet(viewsets.ViewSet,generics.UpdateAPIView,generics.CreateAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            rate = Rate.objects.get(pk=int(response.data['id']))
            rate.user_id = self.request.user
            rate.save()
            return Response(data=RateSerializer(rate).data,status=status.HTTP_201_CREATED)
        except Rate.DoesNotExist as od:
            return Response(data={"error_msg":f"Rate {response.data['id']} not found."},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"error_msg":f"{str(e)}","param_id":kwargs.get("pk")},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
