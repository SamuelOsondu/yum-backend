import uuid
from django.conf import settings
from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from food.models import Profile


class State(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class LocalGovernmentArea(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="address")
    street_address = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    lga = ChainedForeignKey(
        LocalGovernmentArea,
        chained_field="state",
        chained_model_field="state",
        show_all=False,
        auto_choose=True,
        sort=True,
        blank=True,
        null=True,
    )

    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"{self.street_address} - {self.lga} - {self.state}"


class WeightPriceRange(models.Model):
    lga = models.ForeignKey(LocalGovernmentArea, on_delete=models.CASCADE, related_name="weight_ranges")
    min_weight = models.DecimalField(max_digits=5, decimal_places=2)
    max_weight = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
