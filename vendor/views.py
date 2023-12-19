from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from vendor.models import Category, Food, Vendor
from vendor.serializers import CategorySerializer, FoodSerializer, VendorSerializer


class CustomPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class FoodViewSet(ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    pagination_class = CustomPagination


class CategoryFoodViewSet(ModelViewSet):
    serializer_class = FoodSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_pk']

        queryset = Food.objects.filter(category=category_id)
        return queryset


class VendorViewSet(ModelViewSet):
    serializer_class = VendorSerializer
    queryset = Vendor.objects.all()


class VendorFoodViewSet(ModelViewSet):
    serializer_class = FoodSerializer

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_pk']
        queryset = Food.objects.filter(restaurant=vendor_id)

        return queryset
