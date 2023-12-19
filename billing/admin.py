from django.contrib import admin
from .models import LocalGovernmentArea, State, WeightPriceRange


@admin.register(LocalGovernmentArea)
class LocalGovernmentAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    list_filter = ('state',)
    search_fields = ('name', 'state__name')
    ordering = ['name']


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'state__name')
    ordering = ['name']


@admin.register(WeightPriceRange)
class WeightPriceRangeAdmin(admin.ModelAdmin):
    list_display = ('lga', 'min_weight', 'max_weight', 'price')
