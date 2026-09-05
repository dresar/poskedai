from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Category, Product, Supplier, Customer,
    Purchase, PurchaseItem, Sale, SaleItem, StockAdjustment
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'supplier', 'purchase_date', 'total_amount', 'payment_status')
    list_filter = ('payment_status', 'purchase_date')
    search_fields = ('invoice_number', 'supplier__name')
    date_hierarchy = 'purchase_date'
    inlines = [PurchaseItemInline]

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'sale_date', 'total_amount', 'payment_method', 'payment_status')
    list_filter = ('payment_status', 'payment_method', 'sale_date')
    search_fields = ('invoice_number', 'customer__name')
    date_hierarchy = 'sale_date'
    inlines = [SaleItemInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'barcode', 'purchase_price', 'selling_price', 'stock', 'is_low_stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'barcode')
    readonly_fields = ('is_low_stock',)
    list_editable = ('is_active',)
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = _('Stok Rendah')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email')
    search_fields = ('name', 'contact_person', 'phone', 'email')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'phone', 'email')

@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'adjustment_type', 'quantity', 'adjusted_by', 'adjusted_at')
    list_filter = ('adjustment_type', 'adjusted_at')
    search_fields = ('product__name', 'reason')
    date_hierarchy = 'adjusted_at'
