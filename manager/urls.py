from django.urls import path, include
from rest_framework.routers import DefaultRouter

from manager.views import *

# Create a router and register your NewsLetterViewSet with it
router = DefaultRouter()
router.register('news_letter', NewsLetterViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("terms_and_condition/", TermsAndConditionViewSet.as_view(), name="terms_and_condition"),
    path("privacy_policy/", PrivacyPolicyViewSet.as_view(), name="privacy_policy"),
    path("help_centre/", HelpCenterViewSet.as_view(), name="help_centre"),
    path("faqs/", FAQsViewSet.as_view(), name="faqs"),
    path("notification/", NotificationViewSet.as_view(), name="notification"),
    path("socials/", SocialViewSet.as_view(), name="socials")
]

