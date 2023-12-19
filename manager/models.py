from django.conf import settings
from django.db import models

# Create your models here.


class PrivacyPolicy(models.Model):
    privacy_policy = models.TextField()

    def __str__(self):
        return "PRIVACY POLICY"


class TermsAndCondition(models.Model):
    terms_and_condition = models.TextField()

    def __str__(self):
        return "TERMS AND CONDITIONS"


class HelpCenter(models.Model):
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"HELP CENTER - {self.email}"


class Social(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Notification(models.Model):
    user = models.ManyToManyField(settings.AUTH_USER_MODEL)
    notice = models.TextField(max_length=1000)
    attended_to = models.BooleanField(default=False)


class FAQs(models.Model):
    question = models.TextField(max_length=2000)
    answer = models.TextField(max_length=1000)


class NewsLetter(models.Model):
    email = models.EmailField()

