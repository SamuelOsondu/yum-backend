from django.contrib import admin

from manager.models import PrivacyPolicy, Notification, FAQs, NewsLetter, HelpCenter, TermsAndCondition, Social

# Register your models here.

admin.site.register(PrivacyPolicy)
admin.site.register(HelpCenter)
admin.site.register(TermsAndCondition)
admin.site.register(Social)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["notice", "attended_to"]


@admin.register(FAQs)
class FAQsAdmin(admin.ModelAdmin):
    list_display = ["question", "answer"]


@admin.register(NewsLetter)
class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ["email"]
