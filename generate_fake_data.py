import os
import django
import random
import datetime
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile
from faker import Faker

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_kedai.settings')
django.setup()

# Import models after Django setup
from core.models import User
from inventory.models import (
    Category, Product, Supplier, Customer,
    Purchase, PurchaseItem, Sale, SaleItem, StockAdjustment
)

# Initialize Faker
fake = Faker('id_ID')

# Constants
NUM_CATEGORIES = 10
NUM_PRODUCTS = 50
NUM_SUPPLIERS = 15
NUM_CUSTOMERS = 30
NUM_USERS = 5
NUM_PURCHASES = 20
NUM_SALES = 40
NUM_STOCK_ADJUSTMENTS = 15

# Helper function to get random date within range
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)

# Create fake data
@transaction.atomic
def create_fake_data():
    print("Generating fake data...")
    
    # Create superuser if not exists
    if not User.objects.filter(email='admin@example.com').exists():
        User.objects.create_superuser(
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )
        print("Superuser created: admin@example.com / admin123")
    
    # Create users
    users = []
    roles = ['ADMIN', 'CASHIER', 'INVENTORY_MANAGER']
    
    for i in range(NUM_USERS):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name,
                phone_number=fake.phone_number(),
                address=fake.address(),
                role=random.choice(roles),
                is_active=True,
                is_staff=True
            )
            users.append(user)
            print(f"Created user: {email}")
    
    if not users:  # If no new users were created, get existing ones
        users = list(User.objects.all()[:NUM_USERS])
    
    # Create categories
    categories = []
    category_names = [
        "Minuman", "Makanan", "Snack", "Kopi", "Teh", 
        "Dessert", "Roti", "Buah", "Sayuran", "Bumbu", 
        "Bahan Baku", "Alat Dapur", "Kemasan", "Lainnya"
    ]
    
    for i in range(min(NUM_CATEGORIES, len(category_names))):
        name = category_names[i]
        if not Category.objects.filter(name=name).exists():
            category = Category.objects.create(
                name=name,
                description=fake.paragraph(nb_sentences=2)
            )
            categories.append(category)
            print(f"Created category: {name}")
    
    if not categories:  # If no new categories were created, get existing ones
        categories = list(Category.objects.all()[:NUM_CATEGORIES])
    
    # Create suppliers
    suppliers = []
    for i in range(NUM_SUPPLIERS):
        name = fake.company()
        if not Supplier.objects.filter(name=name).exists():
            supplier = Supplier.objects.create(
                name=name,
                contact_person=fake.name(),
                phone=fake.phone_number(),
                email=fake.company_email(),
                address=fake.address()
            )
            suppliers.append(supplier)
            print(f"Created supplier: {name}")
    
    if not suppliers:  # If no new suppliers were created, get existing ones
        suppliers = list(Supplier.objects.all()[:NUM_SUPPLIERS])
    
    # Create customers
    customers = []
    for i in range(NUM_CUSTOMERS):
        name = fake.name()
        if not Customer.objects.filter(name=name).exists():
            customer = Customer.objects.create(
                name=name,
                phone=fake.phone_number(),
                email=fake.email(),
                address=fake.address()
            )
            customers.append(customer)
            print(f"Created customer: {name}")
    
    if not customers:  # If no new customers were created, get existing ones
        customers = list(Customer.objects.all()[:NUM_CUSTOMERS])
    
    # Create products
    products = []
    product_names = [
        "Kopi Hitam", "Kopi Susu", "Cappuccino", "Latte", "Espresso",
        "Americano", "Mocha", "Teh Tarik", "Teh Hijau", "Teh Lemon",
        "Jus Jeruk", "Jus Alpukat", "Jus Mangga", "Jus Strawberry",
        "Milkshake Coklat", "Milkshake Vanilla", "Milkshake Strawberry",
        "Nasi Goreng", "Mie Goreng", "Ayam Goreng", "Ayam Bakar",
        "Sate Ayam", "Soto Ayam", "Bakso", "Gado-gado",
        "Pisang Goreng", "Kentang Goreng", "Roti Bakar", "Pancake",
        "Waffle", "Es Krim Vanilla", "Es Krim Coklat", "Es Krim Strawberry",
        "Brownies", "Cheesecake", "Tiramisu", "Pudding",
        "Keripik Kentang", "Keripik Singkong", "Keripik Pisang",
        "Kacang Goreng", "Popcorn", "Coklat Bar", "Permen",
        "Air Mineral", "Soda", "Cola", "Sprite", "Fanta", "Teh Botol"
    ]
    
    units = ["pcs", "box", "kg", "g", "L", "mL", "pack", "botol", "gelas"]
    
    for i in range(min(NUM_PRODUCTS, len(product_names))):
        name = product_names[i]
        if not Product.objects.filter(name=name).exists():
            purchase_price = Decimal(str(random.uniform(5000, 50000))).quantize(Decimal('0.01'))
            selling_price = purchase_price * Decimal(str(random.uniform(1.2, 2.0))).quantize(Decimal('0.01'))
            
            product = Product.objects.create(
                name=name,
                barcode=f"PRD{i+1:06d}",
                category=random.choice(categories),
                description=fake.paragraph(nb_sentences=2),
                purchase_price=purchase_price,
                selling_price=selling_price,
                stock=random.randint(10, 100),
                min_stock=random.randint(5, 20),
                unit=random.choice(units),
                is_active=random.choice([True, True, True, False])  # 75% chance of being active
            )
            products.append(product)
            print(f"Created product: {name}")
    
    if not products:  # If no new products were created, get existing ones
        products = list(Product.objects.all()[:NUM_PRODUCTS])
    
    # Create purchases
    purchases = []
    start_date = timezone.now() - datetime.timedelta(days=90)
    end_date = timezone.now()
    
    for i in range(NUM_PURCHASES):
        purchase_date = random_date(start_date, end_date)
        supplier = random.choice(suppliers)
        created_by = random.choice(users)
        
        purchase = Purchase.objects.create(
            invoice_number=f"PUR{i+1:06d}",
            supplier=supplier,
            purchase_date=purchase_date,
            total_amount=Decimal('0'),
            paid_amount=Decimal('0'),
            due_amount=Decimal('0'),
            payment_status='UNPAID',
            notes=fake.paragraph(nb_sentences=1),
            created_by=created_by
        )
        
        # Add purchase items
        total_amount = Decimal('0')
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, num_items)
        
        for product in selected_products:
            quantity = random.randint(5, 20)
            unit_price = product.purchase_price
            item_total = unit_price * quantity
            
            PurchaseItem.objects.create(
                purchase=purchase,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=item_total
            )
            
            total_amount += item_total
            
            # Update product stock
            product.stock += quantity
            product.save()
        
        # Update purchase totals
        paid_amount = total_amount if random.random() < 0.7 else Decimal(str(random.uniform(0, float(total_amount)))).quantize(Decimal('0.01'))
        due_amount = total_amount - paid_amount
        
        if paid_amount >= total_amount:
            payment_status = 'PAID'
        elif paid_amount > 0:
            payment_status = 'PARTIAL'
        else:
            payment_status = 'UNPAID'
        
        purchase.total_amount = total_amount
        purchase.paid_amount = paid_amount
        purchase.due_amount = due_amount
        purchase.payment_status = payment_status
        purchase.save()
        
        purchases.append(purchase)
        print(f"Created purchase: {purchase.invoice_number}")
    
    # Create sales
    sales = []
    payment_methods = ['CASH', 'CARD', 'TRANSFER', 'QRIS']
    
    for i in range(NUM_SALES):
        sale_date = random_date(start_date, end_date)
        customer = random.choice(customers) if random.random() < 0.7 else None
        created_by = random.choice(users)
        
        sale = Sale.objects.create(
            invoice_number=f"INV{i+1:06d}",
            customer=customer,
            sale_date=sale_date,
            total_amount=Decimal('0'),
            discount=Decimal('0'),
            tax=Decimal('0'),
            grand_total=Decimal('0'),
            payment_method=random.choice(payment_methods),
            payment_status='PAID',
            notes=fake.paragraph(nb_sentences=1) if random.random() < 0.3 else "",
            created_by=created_by
        )
        
        # Add sale items
        total_amount = Decimal('0')
        num_items = random.randint(1, 8)
        available_products = [p for p in products if p.stock > 0]
        
        if available_products:
            selected_products = random.sample(available_products, min(num_items, len(available_products)))
            
            for product in selected_products:
                max_quantity = min(product.stock, 10)
                quantity = random.randint(1, max_quantity) if max_quantity > 0 else 0
                
                if quantity > 0:
                    unit_price = product.selling_price
                    discount_percent = Decimal(str(random.uniform(0, 0.1))).quantize(Decimal('0.01')) if random.random() < 0.2 else Decimal('0')
                    discount = (unit_price * quantity * discount_percent).quantize(Decimal('0.01'))
                    item_total = (unit_price * quantity - discount).quantize(Decimal('0.01'))
                    
                    # Update product stock manually first
                    product.stock -= quantity
                    product.save()
                    
                    # Create SaleItem without triggering stock update
                    sale_item = SaleItem(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        discount=discount,
                        total_price=item_total
                    )
                    # Save without calling the overridden save method
                    super(SaleItem, sale_item).save()
                    
                    total_amount += item_total
        
        # Apply discount and tax
        discount = (total_amount * Decimal(str(random.uniform(0, 0.05)))).quantize(Decimal('0.01')) if random.random() < 0.3 else Decimal('0')
        tax = (total_amount * Decimal('0.11')).quantize(Decimal('0.01')) if random.random() < 0.7 else Decimal('0')
        grand_total = (total_amount - discount + tax).quantize(Decimal('0.01'))
        
        sale.total_amount = total_amount
        sale.discount = discount
        sale.tax = tax
        sale.grand_total = grand_total
        sale.save()
        
        sales.append(sale)
        print(f"Created sale: {sale.invoice_number}")
    
    # Create stock adjustments
    adjustment_types = ['ADD', 'SUBTRACT']
    reasons = [
        "Barang rusak", "Barang kadaluarsa", "Kesalahan input", 
        "Stok opname", "Barang hilang", "Retur ke supplier",
        "Penyesuaian stok", "Donasi", "Sampel", "Lainnya"
    ]
    
    for i in range(NUM_STOCK_ADJUSTMENTS):
        product = random.choice(products)
        adjustment_type = random.choice(adjustment_types)
        quantity = random.randint(1, 10)
        adjusted_by = random.choice(users)
        adjusted_at = random_date(start_date, end_date)
        
        # Ensure we don't go below 0 for stock
        if adjustment_type == 'SUBTRACT':
            # Refresh product from database to get current stock
            product = Product.objects.get(pk=product.pk)
            if product.stock <= 0:
                # Skip this adjustment or change to ADD
                adjustment_type = 'ADD'
            elif product.stock < quantity:
                quantity = product.stock
        
        if quantity > 0:  # Only create adjustment if quantity is valid
            # For SUBTRACT, manually update stock first to avoid constraint error
            if adjustment_type == 'SUBTRACT':
                # Update product stock manually before creating adjustment
                product.stock -= quantity
                product.save()
                
                # Now create the adjustment without auto-updating stock
                adjustment = StockAdjustment(
                    product=product,
                    adjustment_type=adjustment_type,
                    quantity=quantity,
                    reason=random.choice(reasons),
                    adjusted_by=adjusted_by,
                    adjusted_at=adjusted_at
                )
                # Save without calling the overridden save method
                super(StockAdjustment, adjustment).save()
            else:
                # For ADD, we can use the normal create method
                adjustment = StockAdjustment.objects.create(
                    product=product,
                    adjustment_type=adjustment_type,
                    quantity=quantity,
                    reason=random.choice(reasons),
                    adjusted_by=adjusted_by,
                    adjusted_at=adjusted_at
                )
            
            print(f"Created stock adjustment: {adjustment.id} - {product.name} ({adjustment_type})")
    
    print("\nFake data generation completed!")
    print("\nSummary:")
    print(f"Users: {User.objects.count()}")
    print(f"Categories: {Category.objects.count()}")
    print(f"Products: {Product.objects.count()}")
    print(f"Suppliers: {Supplier.objects.count()}")
    print(f"Customers: {Customer.objects.count()}")
    print(f"Purchases: {Purchase.objects.count()}")
    print(f"Sales: {Sale.objects.count()}")
    print(f"Stock Adjustments: {StockAdjustment.objects.count()}")
    print("\nLogin credentials:")
    print("Admin: admin@example.com / admin123")
    print("Other users: [firstname].[lastname]@example.com / password123")


if __name__ == "__main__":
    create_fake_data()