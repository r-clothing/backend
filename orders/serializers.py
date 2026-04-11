from rest_framework import serializers

from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='variant.product.name',
        read_only=True
    )

    product_image = serializers.SerializerMethodField()

    size = serializers.CharField(
        source='variant.size.value',
        read_only=True
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'variant',
            'quantity',
            'price',
            'size',
            'product_name',
            'product_image',
            'total_price'
        ]

    def get_product_image(self, obj):
        main = obj.variant.product.images.filter(main=True).first()

        return main.url if main else None

    def get_total_price(self, obj):

        return obj.price * obj.quantity

class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_email',
            'name',
            'address',
            'city',
            'postal_code',
            'phone',
            'total_price',
            'status',
            'is_paid',
            'created_at',
            'items'
        ]

        read_only_fields = ['user', 'created_at']
