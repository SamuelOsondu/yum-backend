from rest_framework import serializers

from manager.models import *


class PrivacySerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivacyPolicy
        fields = ["privacy_policy"]


class TermsAndConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndCondition
        fields = ["terms_and_condition"]


class HelpCenterSerializer(serializers.ModelSerializer):

    class Meta:
        model = HelpCenter

        fields = ["phone_number", "email"]


class SocialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Social
        fields = ["name", "url", "icon"]


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification

        fields = ["notice", "attended_to"]


class FAQsSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQs

        fields = ["question", "answer"]


class NewsLetterSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsLetter

        fields = ["email"]

