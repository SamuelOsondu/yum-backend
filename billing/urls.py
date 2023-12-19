from django.urls import path
from .views import LGAsByStateAPIView, BillingPriceAPIView, StatesAPIView

urlpatterns = [
    path('states/<uuid:state_id>/', LGAsByStateAPIView.as_view(), name='lgas-by-state'),
    path('billing-price/', BillingPriceAPIView.as_view(), name='billing-price'),
    path('states/', StatesAPIView.as_view(), name='states'),
]
