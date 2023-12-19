from django.db import transaction
from rest_framework import serializers, status
from rest_framework.response import Response
from billing.models import Address
from food.models import Rating, Favourite, CartFood, Cart, Profile, OrderFood, Order
from vendor.models import Food
from vendor.serializers import FoodSerializer


class FavouriteSerialiizer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    food = FoodSerializer(many=False)
    total_foods = serializers.SerializerMethodField(method_name='get_total_foods')

    class Meta:
        model = Favourite
        fields = ["id", "food", "total_foods"]

    def get_id(self, obj):
        return obj.id

    def get_total_foods(self, obj):
        user = self.context['request'].user

        # Count the number of favorite foods for the given user
        total_foods = Favourite.objects.filter(user=user).count()
        return total_foods

    def to_representation(self, instance):
        return self.fields['food'].to_representation(instance.food)


class CartFoodSerializer(serializers.ModelSerializer):
    price_sub_total = serializers.SerializerMethodField(method_name="total")
    food = FoodSerializer(many=False)

    class Meta:
        model = CartFood
        fields = ["id", "cart", "food", "quantity", "price_sub_total"]

    def total(self, cart_food: CartFood):
        return cart_food.quantity * cart_food.food.price


class AddCartFoodSerializer(serializers.ModelSerializer):
    food_id = serializers.UUIDField()
    quantity = serializers.IntegerField()

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        food_id = self.validated_data["food_id"]
        quantity = self.validated_data["quantity"]

        if quantity is None:
            return Response({"error": "quantity is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_food = CartFood.objects.get(food_id=food_id, cart_id=cart_id)
            cart_food.quantity += quantity
            cart_food.save()

            self.instance = cart_food

        except CartFood.DoesNotExist:
            self.instance = CartFood.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartFood
        fields = ["id", "food_id", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    cart_foods = CartFoodSerializer(many=True, read_only=True)
    price_grand_total = serializers.SerializerMethodField(method_name='price_main_total')
    total_quantity = serializers.SerializerMethodField(method_name='calculate_total_quantity')

    class Meta:
        model = Cart
        fields = ["id", 'cart_foods', 'price_grand_total', 'total_quantity']

    def price_main_total(self, cart: Cart):
        cart_foods = cart.cart_foods.all()
        total = sum([food.quantity * food.food.price for food in cart_foods])
        return total

    def calculate_total_quantity(self, cart: Cart):
        cart_foods = cart.cart_foods.all()
        total_quantity = sum([food.quantity for food in cart_foods])
        return total_quantity


class AddFavouriteSerializer(serializers.Serializer):
    food_id = serializers.UUIDField()

    def save(self, **kwargs):
        food_id = self.validated_data.get('food_id')
        user = self.context['request'].user
        try:
            food = Food.objects.get(id=food_id)
            response_data = {"message": f"The food {food_id} was already favourited"}
            # Check if the food is already in the user's favorites
            if not Favourite.objects.filter(user=user, food=food).exists():
                food.is_favourite.add(user)
                favorite, created = Favourite.objects.get_or_create(user=user, food=food)
                response_data = {
                    "favorite_id": favorite.id,
                    "food_id": food.id,
                    "food_name": food.name,
                }
                return response_data
            return response_data
        except Food.DoesNotExist:
            raise serializers.ValidationError("Food not found")


class RemoveFavouriteSerializer(serializers.Serializer):
    id = serializers.UUIDField()

    def save(self, **kwargs):
        food_id = self.validated_data.get('id')  # Get the food ID from the validated data
        user = self.context['request'].user

        try:
            food = Food.objects.get(id=food_id)
            food.is_favourite.remove(user)
            return food
        except Food.DoesNotExist:
            raise serializers.ValidationError("Food not found")


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    phone_number = serializers.CharField(allow_blank=True, required=False)
    image = serializers.ImageField(allow_empty_file=True, required=False)

    class Meta:
        model = Profile
        fields = ["id", "first_name", "last_name", "image", "phone_number"]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "rating", "description"]

    def create(self, validated_data):
        food_id = self.context["food_id"]
        user_id = self.context["user_id"]

        # Try to get an existing rating, or create a new one if it doesn't exist
        rating, created = Rating.objects.get_or_create(food_id=food_id, user_id=user_id, defaults=validated_data)

        if not created:
            # If the rating already exists, update its fields
            for attr, value in validated_data.foods():
                setattr(rating, attr, value)
            rating.save()

        return rating


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["street_address", "lga", "state", "phone", "email"]


class OrderFoodSerializer(serializers.ModelSerializer):
    food = FoodSerializer(many=False, read_only=True)

    class Meta:
        model = OrderFood
        fields = ["id", "food", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    foods = OrderFoodSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', "placed_at", "status", "owner", "foods"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("This cart_id is invalid")

        elif not CartFood.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError("Sorry your cart is empty")

        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user_id = self.context["user_id"]
            order = Order.objects.create(owner_id=user_id)
            cart_food = CartFood.objects.filter(cart_id=cart_id)

            for cart_food in cart_food:
                OrderFood.objects.create(
                    order=order,
                    food=cart_food.food,
                    quantity=cart_food.quantity
                )

            Cart.objects.filter(id=cart_id).delete()
            return order
