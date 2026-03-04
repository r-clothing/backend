from rest_framework import serializers
from .models import ProductType, ProductImage, Product, ProductVariant, SizeOption


class ProductTypeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ['id', 'name']


class SizeOptionSerializer(serializers.ModelSerializer):
    product_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(),
        source='product_type',
        write_only=True
    )

    product_type = serializers.CharField(
        source='product_type.name',
        read_only=True
    )

    class Meta:
        model = SizeOption
        fields = ['id', 'value', 'product_type', 'product_type_id']


class ProductImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'url', 'main']
        read_only_fields = ['product']


class ProductVariantModelSerializer(serializers.ModelSerializer):
    size = SizeOptionSerializer(read_only=True)

    product = serializers.SerializerMethodField()  # ✅ ADD THIS

    size_id = serializers.PrimaryKeyRelatedField(
        queryset=SizeOption.objects.all(),
        source='size',
        write_only=True
    )

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    final_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'product',   # ✅ NEW (non-breaking)
            'product_id',
            'size',
            'size_id',
            'stock',
            'price',
            'final_price'
        ]

    def get_product(self, obj):
        return {
            "id": obj.product.id,
            "name": obj.product.name,
            "main_image": obj.product.images.filter(main=True).first().url
            if obj.product.images.filter(main=True).exists()
            else None
        }


class ProductModelSerializer(serializers.ModelSerializer):
    product_type = serializers.CharField(source='product_type.name')
    main_image = serializers.SerializerMethodField()
    image = serializers.URLField(write_only=True, required=False)

    images = ProductImageModelSerializer(many=True, read_only=True)
    variants = ProductVariantModelSerializer(many=True, read_only=True)

    available_sizes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'category',
            'product_type',
            'description',
            'price',
            'main_image',
            'images',
            'variants',
            'available_sizes',
            'image',
            'is_active',
            'created_at',
            'updated_at'
        ]

    def get_main_image(self, obj):
        main = obj.images.filter(main=True).first()
        return main.url if main else None

    def get_available_sizes(self, obj):
        return SizeOptionSerializer(
            obj.product_type.sizes.all(),
            many=True
        ).data

    def create(self, validated_data):
        image_url = validated_data.pop('image', None)
        type_name = validated_data.pop('product_type')['name']

        product_type, _ = ProductType.objects.get_or_create(name=type_name)

        product = Product.objects.create(
            product_type=product_type,
            **validated_data
        )

        if image_url:
            ProductImage.objects.create(
                product=product,
                url=image_url,
                main=True
            )

        return product

    def update(self, instance, validated_data):
        image_url = validated_data.pop('image', None)

        if 'product_type' in validated_data:
            type_name = validated_data.pop('product_type')['name']
            product_type, _ = ProductType.objects.get_or_create(name=type_name)
            instance.product_type = product_type

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if image_url:
            ProductImage.objects.create(
                product=instance,
                url=image_url,
                main=False
            )

        return instance