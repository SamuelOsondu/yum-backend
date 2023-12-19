from urllib.parse import urljoin
from django.db.models import Avg
from rest_framework import serializers
from food.models import Rating, Favourite
from vendor.models import Category, MultipleImage, Food, Vendor


class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = ("id", "shop", "phone_number", "address", )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MultipleImage
        fields = ('image1', 'image2', 'image3', 'image4', 'image5')


class FoodSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    additional_images = serializers.SerializerMethodField()
    favorite_id = serializers.SerializerMethodField()

    class Meta:
        model = Food
        fields = ['category', 'id', 'name', 'price', 'new_price', 'description', 'image',  'weight', 'is_favourite',
                  'favorite_id', "average_rating", "additional_images"]

    def get_average_rating(self, obj):
        # Calculate the average rating for the food
        average_rating = Rating.objects.filter(food=obj).aggregate(Avg('rating'))['rating__avg']
        return average_rating

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['average_rating'] = self.get_average_rating(instance)
        return data

    def get_is_favourite(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favourite.objects.filter(user=user, food=obj).exists()
        else:
            return False

    def get_favorite_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            favorite = Favourite.objects.filter(user=user, food=obj).first()
            return favorite.id if favorite else None
        else:
            return None

    def get_additional_images(self, obj):
        request = self.context.get('request')
        base_url = request.build_absolute_uri('/').replace("/api/foods/", "/")

        image_fields = ['image1', 'image2', 'image3', 'image4', 'image5']
        image_urls = []

        # Use .first() to get the first instance of MultipleImage
        additional_images = getattr(obj, 'additional_images', None)

        if additional_images:
            additional_image = additional_images.first()

            if additional_image:
                for field in image_fields:
                    image = getattr(additional_image, field)
                    if image:
                        image_urls.append(urljoin(base_url, image.url))

        return image_urls

