from rest_framework import serializers
from .models import ProductCategory, Product

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.category_name")  # Fetch category name
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), required=False)  # Allow setting category, but optional

    class Meta:
        model = Product
        fields = [
            "product_id", "category", "category_name", "product_name", "description", 
            "price", "stock", "created_at", "updated_at"
        ]

    def validate_price(self, value):
        """Ensure price is a positive number."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value):
        """Ensure stock is a non-negative integer."""
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value
    
    def create(self, validated_data):
        """Ensure default category is assigned if none is provided."""
        if not validated_data.get("category"):
            validated_data["category"] = Product.get_default_category()
        return super().create(validated_data)
