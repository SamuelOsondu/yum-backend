import json
import uuid
import requests
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from food.models import Order, OrderFood
from food.serializers import OrderSerializer, CreateOrderSerializer, OrderFoodSerializer
from yum import settings


def initiate_payment(amount, email, order_id, name):
    url = "https://api.flutterwave.com/v3/payments"
    headers = {
        "Authorization": f"Bearer {settings.FLW_SEC_KEY}"

    }

    data = {
        "tx_ref": str(order_id),
        "amount": str(amount),
        "currency": "NGN",
        "redirect_url": "https://fondstore-buildoptimus.onrender.com/orders/",
        "meta": {
            "consumer_id": 23,
            "consumer_mac": "92a3-912ba-1192a"
        },
        "customer": {
            "email": email,
            "phonenumber": "",
            "name": name,
        },
        "customizations": {
            "title": "FONDSTORE PAYMENTS",
            "logo": "http://www.piedpiper.com/app/themes/joystick-v27/images/logo.png"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        return Response(response_data)

    except requests.exceptions.RequestException as err:
        print("the payment didn't go through")
        return Response({"error": str(err)}, status=500)



class WebhookPermission(BasePermission):
    def has_permission(self, request, view):
        # Implement your custom logic for allowing access
        signature = request.headers.get('verif-hash')
        return signature == settings.FLW_SECRET_HASH


class OrderViewSet(ModelViewSet):

    @action(detail=True, methods=['POST'])
    def pay(self, request, pk):
        order = self.get_object()
        amount = order.total_price
        email = request.user.email
        name = request.user.username

        order_id = str(order.id)
        return initiate_payment(amount, email, order_id, name)

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateOrderSerializer(data=request.data, context={"user_id": self.request.user.id})
            serializer.is_valid(raise_exception=True)
            order = serializer.save()
            serializer = OrderSerializer(order)

            # Commit the transaction if both actions succeed
            transaction.commit()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Rollback the transaction if any action fails
            transaction.rollback()
            return Response({'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(owner=user)


class OrderFoodViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        if "order_pk" in self.kwargs:
            return OrderFood.objects.filter(order_id=self.kwargs["order_pk"])

    def get_serializer_class(self):
        return OrderFoodSerializer

    def get_serializer_context(self):
        # Include the request object and order_id in the context
        context = super().get_serializer_context()
        order_id = self.kwargs.get("order_pk")
        context['order_id'] = order_id
        return context


@csrf_exempt
@action(detail=False, methods=['POST'])
@permission_classes([[WebhookPermission]])
def webhook_handler(request):
    payload = json.loads(request.body.decode('utf-8'))
    signature = request.headers.get('verif-hash')

    # Verify the webhook signature
    if signature != settings.FLW_SECRET_HASH:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Process the webhook payload
    tx_ref = payload.get("data", {}).get("tx_ref")
    status = payload.get("data", {}).get("status")
    if tx_ref:
        try:
            # Update the order only if the status has changed
            order = Order.objects.get(id=tx_ref)
            if order and order.status != status:
                # ReVerify the transaction
                order.status = status
                order.save()
                return JsonResponse({'msg': "Webhook received and processed successfully"}, status=200)

            elif not order:
                return JsonResponse({"msg": "Order not found"}, status=404)
            else:
                return JsonResponse({"msg": "Status is already up to date"}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({"msg": "Order not found"}, status=404)
        except Exception as e:
            error_message = f"Error processing webhook: {str(e)}"
            print(error_message)
            return JsonResponse({"msg": f"Error processing webhook: {str(e)}"}, status=500)
    else:
        return JsonResponse({"msg": "Webhook received, but tx_ref is missing"}, status=400)
