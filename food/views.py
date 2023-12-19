from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from billing.models import Address
from food.models import Cart, CartFood, Favourite, Rating, Profile
from food.serializers import CartSerializer, AddCartFoodSerializer, CartFoodSerializer, AddFavouriteSerializer, \
    RemoveFavouriteSerializer, FavouriteSerialiizer, RatingSerializer, AddressSerializer, ProfileSerializer


class CartViewSet(ModelViewSet):
    http_method_names = ["get", "delete"]
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            # Authenticated user
            cart, _ = Cart.objects.get_or_create(user=user)
            return Cart.objects.filter(pk=cart.pk)
        else:
            # Guest user - Check if there's a guest cart in the session
            cart_id = self.request.session.get('guest_cart_id')
            if cart_id:
                return Cart.objects.filter(pk=cart_id)
            else:
                # Create a new guest cart if it doesn't exist
                cart_id = Cart.objects.create()
                self.request.session['guest_cart_id'] = str(cart_id.pk)
                # Always add this str converter as such so it could be properly serialized.
                return Cart.objects.filter(pk=cart_id.pk)


class CartFoodViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        if "cart_pk" in self.kwargs:
            return CartFood.objects.filter(cart_id=self.kwargs["cart_pk"])
        else:
            # Guest user - Retrieve cart based on session
            cart_id = self.request.session.get('guest_cart_id')
            return CartFood.objects.filter(cart_id=cart_id)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartFoodSerializer
        return CartFoodSerializer

    def get_serializer_context(self):
        # Include the request object and cart_id in the context
        context = super().get_serializer_context()
        cart_id = self.kwargs.get("cart_pk") or self.request.session.get('guest_cart_id')
        context['cart_id'] = cart_id
        return context


class MergeCartsView(APIView):
    def post(self, request):
        user = request.user

        if not user.is_authenticated:
            raise PermissionDenied("Authentication is required to merge carts.")

        try:
            guest_cart = Cart.objects.get(id=request.session.get('guest_cart_id'))
            user_cart, _ = Cart.objects.get_or_create(user=user)
            CartFood.objects.filter(cart=guest_cart).update(cart=user_cart)
            del request.session['guest_cart_id']
        except Cart.DoesNotExist:
            return Response({"message": "Cart Does not exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "A successful merge"}, status=status.HTTP_200_OK)


class FavouriteViewSet(ModelViewSet):
    http_method_names = ["get", "post", "delete"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddFavouriteSerializer
        if self.request.method == "DELETE":
            print("delete")
            return RemoveFavouriteSerializer
        return FavouriteSerialiizer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # Pass the request object to the serializer
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.save()

        # Construct the response with the response data
        return Response(response_data, status=status.HTTP_201_CREATED)


class RatingViewSet(ModelViewSet):
    # queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(cart_id=self.kwargs['cart_pk'])

    def get_serializer_context(self):
        user_id = self.request.user.id
        cart_id = self.kwargs["cart_pk"]
        return {"user_id": user_id, "cart_id": cart_id}


class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return the addresses of the currently authenticated user
        return Address.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = AddressSerializer(data=request.data)

        if serializer.is_valid():
            # Assign the authenticated user as the address's user
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response("Address added successfully", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return the profile of the currently authenticated user
        return Profile.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Check if a profile already exists for the authenticated user
        existing_profile = Profile.objects.filter(user=request.user).first()

        if existing_profile:
            # Update the existing profile with the new data
            serializer = ProfileSerializer(existing_profile, data=request.data)
        else:
            # Create a new profile if it doesn't exist
            serializer = ProfileSerializer(data=request.data)

        if serializer.is_valid():
            # Assign the authenticated user as the profile's user
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response("Profile created or updated successfully", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
