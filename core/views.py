from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from vendor.models import Vendor


class ActivateUser(UserViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())

        # Retrieve uid and token from request.GET
        uid = self.request.GET.get('uid')
        token = self.request.GET.get('token')

        # Pass uid and token to the serializer
        kwargs['data'] = {"uid": uid, "token": token}
        return serializer_class(*args, **kwargs)

    def activation(self, request, *args, **kwargs):
        super().activation(request, *args, **kwargs)

        return Response(status=status.HTTP_200_OK)


class VendorLoginView(LoginView):
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Call Djoser's perform_create to generate the authentication token
        super(VendorLoginView, self).perform_create(serializer)

        # Check if the user is a vendor
        user = self.user
        try:
            vendor_profile = Vendor.objects.get(user=user)
        except Vendor.DoesNotExist:
            # User is not a vendor, delete the authentication token and return an unauthorized response
            self.auth.delete()
            return Response({'detail': 'You are not authorized to log in as a vendor.'}, status=status.HTTP_401_UNAUTHORIZED)

