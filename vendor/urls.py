from django.urls import path, include
from manager.views import FoodSearchAPIView
from .views import *
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register("vendors", VendorViewSet)

router.register("categories", CategoryViewSet, basename='categories')
router.register("foods", FoodViewSet)

category_router = routers.NestedSimpleRouter(router, "categories", lookup="category")
category_router.register(r'foods', CategoryFoodViewSet, basename='categories')

vendor_router = routers.NestedSimpleRouter(router, "vendors", lookup="vendor")
vendor_router.register(r'foods', VendorFoodViewSet, basename='foods')

urlpatterns = [
    path("", include(router.urls)),
    path('', include(category_router.urls)),
    path('', include(vendor_router.urls)),
    path('food_search/', FoodSearchAPIView.as_view(), name='food-search'),
]
