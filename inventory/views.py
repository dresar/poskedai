from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Category, Product, Supplier, Customer, Purchase, PurchaseItem, Sale, SaleItem, StockAdjustment
import json
import csv
import qrcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image
import uuid
import datetime

# Forms
from django import forms

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea w-full rounded-md', 'rows': 3}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'barcode', 'category', 'purchase_price', 'selling_price', 
                 'stock', 'min_stock', 'unit', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'barcode': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'category': forms.Select(attrs={'class': 'form-select w-full rounded-md'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md'}),
            'stock': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md'}),
            'unit': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea w-full rounded-md', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox rounded'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'phone': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'email': forms.EmailInput(attrs={'class': 'form-input w-full rounded-md'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea w-full rounded-md', 'rows': 3}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'phone': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'email': forms.EmailInput(attrs={'class': 'form-input w-full rounded-md'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea w-full rounded-md', 'rows': 3}),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['invoice_number', 'supplier', 'purchase_date', 'total_amount', 
                 'paid_amount', 'due_amount', 'payment_status', 'notes']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-input w-full rounded-md'}),
            'supplier': forms.Select(attrs={'class': 'form-select w-full rounded-md'}),
            'purchase_date': forms.DateTimeInput(attrs={'class': 'form-input w-full rounded-md', 'type': 'datetime-local'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md', 'readonly': 'readonly'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md'}),
            'due_amount': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md', 'readonly': 'readonly'}),
            'payment_status': forms.Select(attrs={'class': 'form-select w-full rounded-md'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea w-full rounded-md', 'rows': 3}),
        }

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select w-full rounded-md'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md'}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'payment_method', 'discount', 'tax', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select w-full rounded-md'}),
            'payment_method': forms.Select(attrs={'class': 'form-select w-full rounded-md'}),
            'discount': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md', 'min': '0'}),
            'tax': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea w-full rounded-md', 'rows': 3}),
        }

class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['product', 'adjustment_type', 'quantity', 'reason']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select w-full rounded-md'}),
            'adjustment_type': forms.Select(attrs={'class': 'form-select w-full rounded-md'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input w-full rounded-md', 'min': '1'}),
            'reason': forms.Textarea(attrs={'class': 'form-textarea w-full rounded-md', 'rows': 3}),
        }

# Category Views
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori berhasil ditambahkan.')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Tambah Kategori'})

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori berhasil diperbarui.')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Edit Kategori'})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Kategori berhasil dihapus.')
        return redirect('inventory:category_list')
    return render(request, 'inventory/confirm_delete.html', {'object': category, 'title': 'Hapus Kategori'})

# Product Views
@login_required
def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock_status', '')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(barcode__icontains=query))
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if stock_status == 'low':
        products = products.filter(stock__lte=F('min_stock'))
    elif stock_status == 'out':
        products = products.filter(stock=0)
    
    categories = Category.objects.all()
    
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'stock_status': stock_status
    })

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Produk berhasil ditambahkan.')
            return redirect('inventory:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Tambah Produk'})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'inventory/product_detail.html', {'product': product})

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produk berhasil diperbarui.')
            return redirect('inventory:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Produk'})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produk berhasil dihapus.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/confirm_delete.html', {'object': product, 'title': 'Hapus Produk'})

@login_required
def import_products(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File harus berformat CSV.')
            return redirect('inventory:import_products')
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                category, _ = Category.objects.get_or_create(name=row['category'])
                
                Product.objects.update_or_create(
                    barcode=row['barcode'] if row['barcode'] else None,
                    defaults={
                        'name': row['name'],
                        'category': category,
                        'purchase_price': float(row['purchase_price']),
                        'selling_price': float(row['selling_price']),
                        'stock': int(row['stock']),
                        'min_stock': int(row['min_stock']),
                        'unit': row['unit'],
                        'description': row['description'],
                        'is_active': row['is_active'].lower() == 'true',
                    }
                )
            
            messages.success(request, 'Produk berhasil diimpor.')
            return redirect('inventory:product_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'inventory/import_products.html')

@login_required
def export_products(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['name', 'barcode', 'category', 'purchase_price', 'selling_price', 
                    'stock', 'min_stock', 'unit', 'description', 'is_active'])
    
    products = Product.objects.all()
    for product in products:
        writer.writerow([
            product.name,
            product.barcode or '',
            product.category.name if product.category else '',
            product.purchase_price,
            product.selling_price,
            product.stock,
            product.min_stock,
            product.unit,
            product.description,
            product.is_active
        ])
    
    return response

@login_required
def generate_barcode(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if not product.barcode:
        # Generate a random barcode if none exists
        product.barcode = str(uuid.uuid4().int)[:12]
        product.save()
    
    # Generate barcode image
    EAN = barcode.get_barcode_class('ean13')
    # Pad to 12 digits and add check digit
    ean = EAN(product.barcode.zfill(12), writer=ImageWriter())
    buffer = BytesIO()
    ean.write(buffer)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{product.name}_barcode.png"'
    return response

@login_required
def generate_qrcode(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"ID: {product.id}\nName: {product.name}\nPrice: {product.selling_price}")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    # Save to product if not exists
    if not product.qr_code:
        from django.core.files.base import ContentFile
        product.qr_code.save(f"{product.name}_qr.png", ContentFile(buffer.getvalue()), save=True)
    
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{product.name}_qrcode.png"'
    return response

# Supplier Views
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier berhasil ditambahkan.')
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Tambah Supplier'})

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    purchases = Purchase.objects.filter(supplier=supplier).order_by('-purchase_date')
    return render(request, 'inventory/supplier_detail.html', {'supplier': supplier, 'purchases': purchases})

@login_required
def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier berhasil diperbarui.')
            return redirect('inventory:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})

@login_required
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier berhasil dihapus.')
        return redirect('inventory:supplier_list')
    return render(request, 'inventory/confirm_delete.html', {'object': supplier, 'title': 'Hapus Supplier'})

# Customer Views
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'inventory/customer_list.html', {'customers': customers})

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pelanggan berhasil ditambahkan.')
            return redirect('inventory:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'inventory/customer_form.html', {'form': form, 'title': 'Tambah Pelanggan'})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    sales = Sale.objects.filter(customer=customer).order_by('-sale_date')
    return render(request, 'inventory/customer_detail.html', {'customer': customer, 'sales': sales})

@login_required
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pelanggan berhasil diperbarui.')
            return redirect('inventory:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'inventory/customer_form.html', {'form': form, 'title': 'Edit Pelanggan'})

@login_required
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Pelanggan berhasil dihapus.')
        return redirect('inventory:customer_list')
    return render(request, 'inventory/confirm_delete.html', {'object': customer, 'title': 'Hapus Pelanggan'})

# Purchase Views
@login_required
def purchase_list(request):
    purchases = Purchase.objects.all().order_by('-purchase_date')
    return render(request, 'inventory/purchase_list.html', {'purchases': purchases})

@login_required
def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            purchase.save()
            
            # Process purchase items from JSON data
            items_data = json.loads(request.POST.get('items_data', '[]'))
            for item_data in items_data:
                product = Product.objects.get(pk=item_data['product_id'])
                quantity = int(item_data['quantity'])
                unit_price = float(item_data['unit_price'])
                
                # Create purchase item
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=quantity * unit_price
                )
                
                # Update product stock
                product.stock += quantity
                product.save()
            
            messages.success(request, 'Pembelian berhasil ditambahkan.')
            return redirect('inventory:purchase_detail', pk=purchase.pk)
    else:
        form = PurchaseForm(initial={'invoice_number': f'PO-{timezone.now().strftime("%Y%m%d%H%M%S")}'})    
    
    products = Product.objects.all()
    return render(request, 'inventory/purchase_form.html', {
        'form': form, 
        'products': products,
        'title': 'Tambah Pembelian'
    })

@login_required
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    items = purchase.items.all()
    return render(request, 'inventory/purchase_detail.html', {'purchase': purchase, 'items': items})

@login_required
def edit_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pembelian berhasil diperbarui.')
            return redirect('inventory:purchase_detail', pk=purchase.pk)
    else:
        form = PurchaseForm(instance=purchase)
    
    items = purchase.items.all()
    return render(request, 'inventory/purchase_edit.html', {
        'form': form, 
        'purchase': purchase,
        'items': items,
        'title': 'Edit Pembelian'
    })

@login_required
def delete_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        # Revert stock changes
        for item in purchase.items.all():
            product = item.product
            product.stock -= item.quantity
            product.save()
        
        purchase.delete()
        messages.success(request, 'Pembelian berhasil dihapus.')
        return redirect('inventory:purchase_list')
    return render(request, 'inventory/confirm_delete.html', {'object': purchase, 'title': 'Hapus Pembelian'})

# Sale / POS Views
@login_required
def pos(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.created_by = request.user
            
            # Calculate total from items
            items_data = json.loads(request.POST.get('items_data', '[]'))
            total_amount = sum(float(item['total_price']) for item in items_data)
            
            sale.total_amount = total_amount
            sale.grand_total = total_amount - sale.discount + sale.tax
            sale.save()
            
            # Process sale items
            for item_data in items_data:
                product = Product.objects.get(pk=item_data['product_id'])
                quantity = int(item_data['quantity'])
                unit_price = float(item_data['unit_price'])
                discount = float(item_data.get('discount', 0))
                
                # Create sale item
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount=discount,
                    total_price=(quantity * unit_price) - discount
                )
            
            messages.success(request, 'Penjualan berhasil ditambahkan.')
            return redirect('inventory:sale_invoice', pk=sale.pk)
    else:
        form = SaleForm()
    
    products = Product.objects.filter(is_active=True, stock__gt=0)
    customers = Customer.objects.all()
    
    return render(request, 'inventory/pos.html', {
        'form': form,
        'products': products,
        'customers': customers
    })

@login_required
def sale_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payment_method = request.GET.get('payment_method')
    
    sales = Sale.objects.all().order_by('-sale_date')
    
    if start_date:
        sales = sales.filter(sale_date__gte=datetime.datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
        sales = sales.filter(sale_date__lte=end_date_obj)
    
    if payment_method:
        sales = sales.filter(payment_method=payment_method)
    
    paginator = Paginator(sales, 10)  # Show 10 sales per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/sale_list.html', {
        'page_obj': page_obj,
        'start_date': start_date,
        'end_date': end_date,
        'payment_method': payment_method
    })

@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    items = sale.items.all()
    return render(request, 'inventory/sale_detail.html', {'sale': sale, 'items': items})

@login_required
def sale_invoice(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    items = sale.items.all()
    return render(request, 'inventory/sale_invoice.html', {'sale': sale, 'items': items})

@login_required
def delete_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        # Revert stock changes
        for item in sale.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        
        sale.delete()
        messages.success(request, 'Penjualan berhasil dihapus.')
        return redirect('inventory:sale_list')
    return render(request, 'inventory/confirm_delete.html', {'object': sale, 'title': 'Hapus Penjualan'})

# Stock Adjustment Views
@login_required
def stock_adjustment_list(request):
    adjustments = StockAdjustment.objects.all().order_by('-adjusted_at')
    return render(request, 'inventory/stock_adjustment_list.html', {'adjustments': adjustments})

@login_required
def add_stock_adjustment(request):
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.adjusted_by = request.user
            adjustment.save()
            messages.success(request, 'Penyesuaian stok berhasil ditambahkan.')
            return redirect('inventory:stock_adjustment_list')
    else:
        form = StockAdjustmentForm()
    
    products = Product.objects.all()
    return render(request, 'inventory/stock_adjustment_form.html', {
        'form': form,
        'products': products,
        'title': 'Tambah Penyesuaian Stok'
    })

# Report Views
@login_required
def report(request):
    return render(request, 'inventory/report.html')

@login_required
def sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    sales = Sale.objects.all()
    
    if start_date:
        sales = sales.filter(sale_date__gte=datetime.datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
        sales = sales.filter(sale_date__lte=end_date_obj)
    
    # Calculate summary data
    total_sales = sales.count()
    total_revenue = sales.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    
    # Get top selling products
    top_products = SaleItem.objects.filter(sale__in=sales).values('product__name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_quantity')[:10]
    
    # Get sales by payment method
    payment_methods = sales.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('grand_total')
    ).order_by('payment_method')
    
    # Get daily sales for chart
    daily_sales = sales.values('sale_date__date').annotate(
        count=Count('id'),
        total=Sum('grand_total')
    ).order_by('sale_date__date')
    
    return render(request, 'inventory/sales_report.html', {
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'top_products': top_products,
        'payment_methods': payment_methods,
        'daily_sales': daily_sales
    })

@login_required
def stock_report(request):
    # Get low stock products
    low_stock_products = Product.objects.filter(stock__lte=F('min_stock'))
    
    # Get out of stock products
    out_of_stock_products = Product.objects.filter(stock=0)
    
    # Get stock value
    products = Product.objects.all()
    total_stock_value = sum(product.stock * product.purchase_price for product in products)
    
    # Get stock by category
    categories = Category.objects.all()
    category_stock = []
    for category in categories:
        products_in_category = Product.objects.filter(category=category)
        total_items = products_in_category.count()
        total_quantity = products_in_category.aggregate(Sum('stock'))['stock__sum'] or 0
        total_value = sum(product.stock * product.purchase_price for product in products_in_category)
        
        category_stock.append({
            'category': category,
            'total_items': total_items,
            'total_quantity': total_quantity,
            'total_value': total_value
        })
    
    return render(request, 'inventory/stock_report.html', {
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_stock_value': total_stock_value,
        'category_stock': category_stock
    })

# API Views for AJAX
@login_required
def api_product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(barcode__icontains=query))
    
    products_data = [{
        'id': product.id,
        'name': product.name,
        'barcode': product.barcode or '',
        'category': product.category.name if product.category else '',
        'selling_price': float(product.selling_price),
        'purchase_price': float(product.purchase_price),
        'stock': product.stock,
        'unit': product.unit
    } for product in products[:20]]  # Limit to 20 results
    
    return JsonResponse({'products': products_data})

@login_required
def api_product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    product_data = {
        'id': product.id,
        'name': product.name,
        'barcode': product.barcode or '',
        'category': product.category.name if product.category else '',
        'selling_price': float(product.selling_price),
        'purchase_price': float(product.purchase_price),
        'stock': product.stock,
        'unit': product.unit
    }
    
    return JsonResponse(product_data)

@csrf_exempt
@login_required
def api_scan_barcode(request):
    barcode = request.POST.get('barcode', '')
    
    try:
        product = Product.objects.get(barcode=barcode)
        product_data = {
            'id': product.id,
            'name': product.name,
            'barcode': product.barcode,
            'category': product.category.name if product.category else '',
            'selling_price': float(product.selling_price),
            'purchase_price': float(product.purchase_price),
            'stock': product.stock,
            'unit': product.unit
        }
        return JsonResponse({'success': True, 'product': product_data})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produk dengan barcode tersebut tidak ditemukan.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
