import uuid
from django.db import models
from core.models import User
from vendor.models import Food
from yum import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to="profile/", blank=True, null=True)
    phone_number = models.CharField(max_length=14, blank=True)

    def __str__(self):
        return self.first_name


class Favourite(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    def __str__(self):
        return self.food.name


class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class CartFood(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_foods")
    food = models.ForeignKey(Food, related_name="cart_foods", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)


class Rating(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='rating')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(choices=((1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('food', 'user')

    def __str__(self):
        return f"{self.user}'s {self.rating}-star rating for {self.food}"


class Order(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Complete'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')

    placed_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.status} - {self.owner}"

    @property
    def total_price(self):
        foods = self.order_foods.all()
        total = sum([food.quantity * food.food.price for food in foods])
        return total


class OrderFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_foods")
    food = models.ForeignKey(Food, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.food.name

