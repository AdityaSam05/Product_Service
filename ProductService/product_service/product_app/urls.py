from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, ProductViewSet

# Creating routers for standard CRUD endpoints
router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    # Include the default ViewSet routes
    path('', include(router.urls)),

    # Custom API endpoints for Products
    path('products/low_stock/', ProductViewSet.as_view({'get': 'low_stock_products'}), name='low-stock-products'),
    path('products/update_stock/<int:pk>/', ProductViewSet.as_view({'patch': 'update_stock'}), name='update-stock'),
    path('products/filter_by_category_and_price/', ProductViewSet.as_view({'get': 'filter_by_category_and_price'}), name='filter-by-category-price'),
    path('products/bulk_delete/', ProductViewSet.as_view({'delete': 'bulk_delete'}), name='bulk-delete'),
    # GET /categories/
    # GET /categories/{id}/
    # POST /categories/
    # PUT /categories/{id}/
    # DELETE /categories/{id}/
    # GET /products/
    # GET /products/{id}/
    # POST /products/
    # PUT /products/{id}/
    # DELETE /products/{id}/
    # GET /products/low_stock/
    # PATCH /products/update_stock/{id}/
    # GET /products/filter_by_category_and_price/
    # DELETE /products/bulk_delete/
]
