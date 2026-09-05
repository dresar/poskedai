from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Category
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    
    # Product
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('products/import/', views.import_products, name='import_products'),
    path('products/export/', views.export_products, name='export_products'),
    path('products/<int:pk>/generate-barcode/', views.generate_barcode, name='generate_barcode'),
    path('products/<int:pk>/generate-qrcode/', views.generate_qrcode, name='generate_qrcode'),
    
    # Supplier
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/<int:pk>/delete/', views.delete_supplier, name='delete_supplier'),
    
    # Customer
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:pk>/delete/', views.delete_customer, name='delete_customer'),
    
    # Purchase
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/add/', views.add_purchase, name='add_purchase'),
    path('purchases/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('purchases/<int:pk>/edit/', views.edit_purchase, name='edit_purchase'),
    path('purchases/<int:pk>/delete/', views.delete_purchase, name='delete_purchase'),
    
    # Sale / POS
    path('pos/', views.pos, name='pos'),
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/invoice/', views.sale_invoice, name='sale_invoice'),
    path('sales/<int:pk>/delete/', views.delete_sale, name='delete_sale'),
    
    # Stock Adjustment
    path('stock-adjustments/', views.stock_adjustment_list, name='stock_adjustment_list'),
    path('stock-adjustments/add/', views.add_stock_adjustment, name='add_stock_adjustment'),
    
    # Reports
    path('reports/', views.report, name='report'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/stock/', views.stock_report, name='stock_report'),
    
    # API endpoints for AJAX
    path('api/products/', views.api_product_list, name='api_product_list'),
    path('api/products/<int:pk>/', views.api_product_detail, name='api_product_detail'),
    path('api/scan-barcode/', views.api_scan_barcode, name='api_scan_barcode'),
]