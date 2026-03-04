from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework.backends import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import ProductType, Product, ProductVariant
from .serializers import (
    ProductTypeModelSerializer,
    ProductModelSerializer,
    ProductVariantModelSerializer,
    ProductImageModelSerializer
)


class ProductTypeAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request, pk=None):
        if pk:
            product_type = get_object_or_404(ProductType, pk=pk)
            serializer = ProductTypeModelSerializer(product_type)
            return Response(serializer.data, status=status.HTTP_200_OK)

        product_types = ProductType.objects.all()
        serializer = ProductTypeModelSerializer(product_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductTypeModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None):
        product_type = get_object_or_404(ProductType, pk=pk)
        serializer = ProductTypeModelSerializer(product_type, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        product_type = get_object_or_404(ProductType, pk=pk)
        serializer = ProductTypeModelSerializer(product_type, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        product_type = get_object_or_404(ProductType, pk=pk)
        product_type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductAPIView(APIView):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'product_type__name', 'description']
    filterset_fields = ['category', 'product_type__name']
    ordering_fields = ['name', 'price']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        return Product.objects.select_related('product_type').prefetch_related(
            'images',
            'variants__size',
            'product_type__sizes'
        )

    def get(self, request, pk=None):
        if pk:
            product = get_object_or_404(self.get_queryset(), pk=pk)
            serializer = ProductModelSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

        queryset = self.filter_queryset(self.get_queryset())
        serializer = ProductModelSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # 🔥 Auto-create variants for all sizes of the product type
        sizes = product.product_type.sizes.all()
        for size in sizes:
            ProductVariant.objects.get_or_create(
                product=product,
                size=size,
                defaults={'stock': 0}
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductModelSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductModelSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductVariantAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        return ProductVariant.objects.select_related(
            'product',
            'size',
            'size__product_type'
        )

    def get(self, request, pk=None):
        if pk:
            product_variant = get_object_or_404(self.get_queryset(), pk=pk)
            serializer = ProductVariantModelSerializer(product_variant)
            return Response(serializer.data, status=status.HTTP_200_OK)

        product_id = request.query_params.get('product_id')

        queryset = self.get_queryset()

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        serializer = ProductVariantModelSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductVariantModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None):
        product_variant = get_object_or_404(ProductVariant, pk=pk)
        serializer = ProductVariantModelSerializer(product_variant, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        product_variant = get_object_or_404(ProductVariant, pk=pk)
        serializer = ProductVariantModelSerializer(product_variant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        product_variant = get_object_or_404(ProductVariant, pk=pk)
        product_variant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageAPIView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request, product_id=None, image_id=None):
        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, pk=product_id)

        if image_id:
            image = get_object_or_404(product.images.all(), pk=image_id)
            serializer = ProductImageModelSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        images = product.images.all()
        serializer = ProductImageModelSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, product_id=None):
        product = get_object_or_404(Product, pk=product_id)
        serializer = ProductImageModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, product_id=None, image_id=None):
        product = get_object_or_404(Product, pk=product_id)
        image = get_object_or_404(product.images.all(), pk=image_id)

        serializer = ProductImageModelSerializer(image, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get('main') is True:
            product.images.update(main=False)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, product_id=None, image_id=None):
        product = get_object_or_404(Product, pk=product_id)
        image = get_object_or_404(product.images.all(), pk=image_id)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
