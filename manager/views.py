from rest_framework import status, generics
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
# from api.models import Food
# from api.serializers import FoodSerializer
from manager.serializers import *
from django.db.models import F, Func, Value, TextField
from django.db.models.functions import Concat

from vendor.models import Food
from vendor.serializers import FoodSerializer


class FoodSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('query', None)
        results = []

        if query:
            # Use annotate to create a computed field for the concatenated value
            foods = Food.objects.annotate(
                concatenated_value=Concat('name', Value(' '), 'description', output_field=TextField())
            ).filter(concatenated_value__icontains=query)

            serializer = FoodSerializer(foods, many=True, context={'request': request})
            results = serializer.data

        response_data = {
            'query': query,
            'results': results
        }

        return Response(response_data, status=status.HTTP_200_OK)


class PrivacyPolicyViewSet(generics.ListAPIView):
    serializer_class = PrivacySerializer
    queryset = PrivacyPolicy.objects.all()


class TermsAndConditionViewSet(generics.ListAPIView):
    serializer_class = TermsAndConditionSerializer
    queryset = TermsAndCondition.objects.all()


class HelpCenterViewSet(generics.ListAPIView):
    serializer_class = HelpCenterSerializer
    queryset = HelpCenter.objects.all()


class SocialViewSet(generics.ListAPIView):
    serializer_class = SocialSerializer
    queryset = Social.objects.all()


class FAQsViewSet(generics.ListAPIView):
    serializer_class = FAQsSerializer
    queryset = FAQs.objects.all()


class NewsLetterViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = NewsLetterSerializer
    queryset = NewsLetter.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Successfully created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
