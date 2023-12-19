from django.urls import path, include
from rest_framework_nested import routers
from food.views import FavouriteViewSet, CartViewSet, CartFoodViewSet, MergeCartsView, RatingViewSet, AddressViewSet, \
    ProfileViewSet
from payment.views import OrderViewSet, OrderFoodViewSet, webhook_handler
from vendor.views import FoodViewSet

router = routers.DefaultRouter()
router.register("foods", FoodViewSet)
router.register("favourites", FavouriteViewSet, basename='favourites')
router.register("address", AddressViewSet, basename="address")
router.register("profile", ProfileViewSet, basename="profile")

router.register("cart", CartViewSet, basename="carts")
cart_router = routers.NestedSimpleRouter(router, "cart", lookup="cart")
cart_router.register(r'cart_food', CartFoodViewSet, basename="cart_foods")

food_router = routers.NestedSimpleRouter(router, "foods", lookup='food')
food_router.register("ratings", RatingViewSet, basename="rating")

# order
router.register("orders", OrderViewSet, basename="orders")
order_router = routers.NestedSimpleRouter(router, "orders", lookup="orders")
order_router.register(r'order_foods', OrderFoodViewSet, basename="order_foods")


urlpatterns = [
    path("", include(router.urls)),
    path('', include(cart_router.urls)),
    path('', include(food_router.urls)),
    path('', include(order_router.urls)),

    path('merge_carts/', MergeCartsView.as_view()),
    path('webhook_handler/', webhook_handler, name='webhook_handler'),
]
