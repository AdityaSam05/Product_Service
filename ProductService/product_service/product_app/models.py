from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class ProductCategory(models.Model):
    id = models.AutoField(primary_key=True, db_column="CATEGORY_ID")  # Match Snowflake PK column
    category_name = models.CharField(max_length=100, unique=True, db_column="CATEGORY_NAME")  # Exact column name

    class Meta:
        db_table = "PRODUCT_APP_PRODUCTCATEGORY"  # Exact Snowflake table name

    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True, db_column="PRODUCT_ID")

    def get_default_category():
        """Fetch or create the default category."""
        return ProductCategory.objects.filter(category_name="Default Category").first() or ProductCategory.objects.create(category_name="Default Category")




    category = models.ForeignKey(
    ProductCategory, 
    on_delete=models.CASCADE, 
    related_name="products",
    db_column="CATEGORY_ID",  # Fix the Snowflake column name
    default=get_default_category  
)
    product_name = models.CharField(max_length=255, db_column="PRODUCT_NAME")
    description = models.TextField(db_column="DESCRIPTION", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column="PRICE")
    stock = models.PositiveIntegerField(db_column="STOCK", default=0)  # Ensuring stock has a default value
    created_at = models.DateTimeField(auto_now_add=True, db_column="CREATED_AT")
    updated_at = models.DateTimeField(auto_now=True, db_column="UPDATED_AT")

    class Meta:
        db_table = "PRODUCT_APP_PRODUCT"

    def __str__(self):
        return self.product_name
