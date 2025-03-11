from rest_framework.exceptions import APIException

class DuplicateProductException(APIException):
    status_code = 400
    default_detail = "Product with this name already exists in the category."
    default_code = "duplicate_product"

class InvalidQuantityException(APIException):
    status_code = 400
    default_detail = "Invalid quantity provided."
    default_code = "invalid_quantity"

class NoProductIDsProvidedException(APIException):
    status_code = 400
    default_detail = "No product IDs provided."
    default_code = "no_product_ids_provided"
