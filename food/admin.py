from django.contrib import admin
from django.contrib.auth.models import Permission
from food.models import *

admin.site.register(Profile)
admin.site.register(Favourite)
admin.site.register(Cart)
admin.site.register(CartFood)
admin.site.register(Rating)
admin.site.register(Order)
admin.site.register(OrderFood)
