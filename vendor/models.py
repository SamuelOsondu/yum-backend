import uuid

from django.db import models

from yum import settings


# The vendor should be added by the admin in the admin page, then they have a special page that displays their
# foods, orders and they can add their foods too
# But now, I have to restrict the login to that page to only vendors.


class Vendor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.shop


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Food(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(max_length=200)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to="foods")
    is_favourite = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favorite_food', blank=True)

    def __str__(self):
        return self.name


class MultipleImage(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="additional_images")
    image1 = models.ImageField(upload_to="additional_image", null=True, blank=True)
    image2 = models.ImageField(upload_to="additional_image", null=True, blank=True)
    image3 = models.ImageField(upload_to="additional_image", null=True, blank=True)
    image4 = models.ImageField(upload_to="additional_image", null=True, blank=True)
    image5 = models.ImageField(upload_to="additional_image", null=True, blank=True)

    def __str__(self):
        return f'{self.food.name} additional images'
