from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission, SAFE_METHODS
from rest_framework.throttling import UserRateThrottle
from django.db.models import Q
from .models import ProductCategory, Product
from .serializers import ProductCategorySerializer, ProductSerializer
from django.core.exceptions import ValidationError
from .exceptions import (
    DuplicateProductException,
    InvalidQuantityException,
    NoProductIDsProvidedException,
)

class CustomThrottle(UserRateThrottle):
    rate = "10000/min"  # Allow 10000 requests per minute per user

class AdminOnlyForWrite(BasePermission):
    """
    Custom permission to allow only admin users to modify data,
    while allowing GET requests for all users.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # Allow GET, HEAD, OPTIONS requests for all users
            return True
        return request.user and request.user.is_staff  # Restrict other methods to admin users

class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Product Categories.
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["category_name"]
    permission_classes = [IsAuthenticatedOrReadOnly, AdminOnlyForWrite]

    def get_throttles(self):
        if self.request.method in SAFE_METHODS:
            return [CustomThrottle()]
        return []

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["product_name", "category__id"]
    permission_classes = [IsAuthenticatedOrReadOnly, AdminOnlyForWrite]

    def get_throttles(self):
        if self.request.method in SAFE_METHODS:
            return [CustomThrottle()]
        return []

    def create(self, request, *args, **kwargs):
        """
        Custom create method to check for duplicate product names in a category.
        """
        category_id = request.data.get("category")
        product_name = request.data.get("product_name")

        if Product.objects.filter(category_id=category_id, product_name=product_name).exists():
            raise DuplicateProductException()

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticatedOrReadOnly])
    def low_stock_products(self, request):
        """
        Retrieve products that have low stock (stock < 10).
        """
        low_stock = Product.objects.filter(stock__lt=10)
        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticatedOrReadOnly, AdminOnlyForWrite])
    def update_stock(self, request, pk=None):
        """
        Update the stock quantity of a product.
        """
        product = self.get_object()
        new_stock = request.data.get("stock")

        try:
            new_stock = int(new_stock)
            if new_stock < 0:
                raise InvalidQuantityException()
        except (ValueError, TypeError):
            raise InvalidQuantityException()

        product.stock = new_stock
        product.save()
        return Response({"message": "Stock updated successfully", "new_stock": product.stock})

    @action(detail=False, methods=["get"], url_path="filter_by_category_and_price", permission_classes=[IsAuthenticatedOrReadOnly])
    def filter_by_category_and_price(self, request):
        """
        Filter products by category ID and optional price range.
        Example: /product/products/filter_by_category_and_price/?category_id=2&min_price=100&max_price=500
        """
        category_id = request.query_params.get("category_id")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        products = Product.objects.all()

        if category_id:
            products = products.filter(category__id=category_id)

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticatedOrReadOnly, AdminOnlyForWrite])
    def bulk_delete(self, request):
        """
        Delete multiple products based on provided IDs.
        """
        product_ids = request.data.get("product_ids", [])

        if not product_ids:
            raise NoProductIDsProvidedException()

        deleted_count, _ = Product.objects.filter(product_id__in=product_ids).delete()
        return Response({"message": f"Deleted {deleted_count} products successfully."}, status=status.HTTP_200_OK)
