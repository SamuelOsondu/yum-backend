from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from food.models import Food, Cart
from food.serializers import CartSerializer
from billing.models import LocalGovernmentArea, State, WeightPriceRange
from billing.serializers import LocalGovernmentAreaSerializer, StateSerializer


class StatesAPIView(APIView):
    def get(self, request):
        states = State.objects.all()  # Retrieve all states
        serializer = StateSerializer(states, many=True)
        return Response({"states": serializer.data})


class LGAsByStateAPIView(APIView):
    def get(self, request, state_id):
        lgas = LocalGovernmentArea.objects.filter(state_id=state_id)
        serializer = LocalGovernmentAreaSerializer(lgas, many=True)
        return Response({"lgas": serializer.data})


class BillingPriceAPIView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        cart_id = request.data.get("cart_id")
        lga_id = request.data.get("lga_id")

        if not lga_id:
            return Response({"error": "LGA ID is required in the request data."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(id=cart_id)
            cart_serializer = CartSerializer(cart, context={'request': request})
            cart_grand_total = cart_serializer.data['price_grand_total']

            total_price = 0

            for cart_food in cart.cart_foods.all():
                food = cart_food.food
                quantity = cart_food.quantity

                pricing_range = WeightPriceRange.objects.filter(
                    lga_id=lga_id, min_weight__lte=food.weight,
                    max_weight__gte=food.weight
                ).first()

                if pricing_range:
                    calculated_price = pricing_range.price * quantity
                    total_price += calculated_price

            sum_total = cart_grand_total + total_price

            response_data = {
                "cart_grand_total": cart_grand_total,
                "billing_total": total_price,
                "sum_total": sum_total
            }

            return Response(response_data)

        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        except WeightPriceRange.DoesNotExist:
            return Response({"error": "Pricing not found for one or more foods in the cart."},
                            status=status.HTTP_404_NOT_FOUND)
