from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone

class Category(models.Model):
    """Model untuk kategori produk"""
    name = models.CharField(_('nama kategori'), max_length=100)
    description = models.TextField(_('deskripsi'), blank=True)
    created_at = models.DateTimeField(_('dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('diperbarui pada'), auto_now=True)
    
    class Meta:
        verbose_name = _('kategori')
        verbose_name_plural = _('kategori')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Model untuk produk"""
    name = models.CharField(_('nama produk'), max_length=255)
    barcode = models.CharField(_('barcode'), max_length=100, unique=True, blank=True, null=True)
    qr_code = models.ImageField(_('QR code'), upload_to='qr_codes/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name=_('kategori'))
    purchase_price = models.DecimalField(_('harga beli'), max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(_('harga jual'), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(_('stok'))
    min_stock = models.PositiveIntegerField(_('stok minimum'), default=5)
    unit = models.CharField(_('satuan'), max_length=50, default='pcs')
    description = models.TextField(_('deskripsi'), blank=True)
    image = models.ImageField(_('gambar'), upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(_('aktif'), default=True)
    created_at = models.DateTimeField(_('dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('diperbarui pada'), auto_now=True)
    
    class Meta:
        verbose_name = _('produk')
        verbose_name_plural = _('produk')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_low_stock(self):
        return self.stock <= self.min_stock

class Supplier(models.Model):
    """Model untuk supplier"""
    name = models.CharField(_('nama supplier'), max_length=255)
    contact_person = models.CharField(_('kontak person'), max_length=255, blank=True)
    phone = models.CharField(_('telepon'), max_length=20)
    email = models.EmailField(_('email'), blank=True)
    address = models.TextField(_('alamat'))
    created_at = models.DateTimeField(_('dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('diperbarui pada'), auto_now=True)
    
    class Meta:
        verbose_name = _('supplier')
        verbose_name_plural = _('supplier')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    """Model untuk pelanggan"""
    name = models.CharField(_('nama pelanggan'), max_length=255)
    phone = models.CharField(_('telepon'), max_length=20, blank=True)
    email = models.EmailField(_('email'), blank=True)
    address = models.TextField(_('alamat'), blank=True)
    created_at = models.DateTimeField(_('dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('diperbarui pada'), auto_now=True)
    
    class Meta:
        verbose_name = _('pelanggan')
        verbose_name_plural = _('pelanggan')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Purchase(models.Model):
    """Model untuk pembelian dari supplier"""
    invoice_number = models.CharField(_('nomor faktur'), max_length=100, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases', verbose_name=_('supplier'))
    purchase_date = models.DateTimeField(_('tanggal pembelian'), default=timezone.now)
    total_amount = models.DecimalField(_('total pembelian'), max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(_('jumlah dibayar'), max_digits=12, decimal_places=2)
    due_amount = models.DecimalField(_('jumlah hutang'), max_digits=12, decimal_places=2)
    payment_status = models.CharField(
        _('status pembayaran'),
        max_length=20,
        choices=[
            ('PAID', _('Lunas')),
            ('PARTIAL', _('Sebagian')),
            ('UNPAID', _('Belum Dibayar')),
        ],
        default='UNPAID'
    )
    notes = models.TextField(_('catatan'), blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='purchases', verbose_name=_('dibuat oleh'))
    created_at = models.DateTimeField(_('dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('diperbarui pada'), auto_now=True)
    
    class Meta:
        verbose_name = _('pembelian')
        verbose_name_plural = _('pembelian')
        ordering = ['-purchase_date']
    
    def __str__(self):
        return self.invoice_number

class PurchaseItem(models.Model):
    """Model untuk item pembelian"""
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items', verbose_name=_('pembelian'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_items', verbose_name=_('produk'))
    quantity = models.PositiveIntegerField(_('jumlah'))
    unit_price = models.DecimalField(_('harga satuan'), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_('total harga'), max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = _('item pembelian')
        verbose_name_plural = _('item pembelian')
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.unit}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Sale(models.Model):
    """Model untuk penjualan"""
    invoice_number = models.CharField(_('nomor faktur'), max_length=100, unique=True, default=uuid.uuid4)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales', verbose_name=_('pelanggan'))
    sale_date = models.DateTimeField(_('tanggal penjualan'), default=timezone.now)
    total_amount = models.DecimalField(_('total penjualan'), max_digits=12, decimal_places=2)
    discount = models.DecimalField(_('diskon'), max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(_('pajak'), max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(_('grand total'), max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        _('metode pembayaran'),
        max_length=20,
        choices=[
            ('CASH', _('Tunai')),
            ('CARD', _('Kartu')),
            ('TRANSFER', _('Transfer')),
            ('QRIS', _('QRIS')),
        ],
        default='CASH'
    )
    payment_status = models.CharField(
        _('status pembayaran'),
        max_length=20,
        choices=[
            ('PAID', _('Lunas')),
            ('PARTIAL', _('Sebagian')),
            ('UNPAID', _('Belum Dibayar')),
        ],
        default='PAID'
    )
    notes = models.TextField(_('catatan'), blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sales', verbose_name=_('dibuat oleh'))
    created_at = models.DateTimeField(_('dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('diperbarui pada'), auto_now=True)
    
    class Meta:
        verbose_name = _('penjualan')
        verbose_name_plural = _('penjualan')
        ordering = ['-sale_date']
    
    def __str__(self):
        return self.invoice_number
    
    def save(self, *args, **kwargs):
        self.grand_total = self.total_amount - self.discount + self.tax
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    """Model untuk item penjualan"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name=_('penjualan'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sale_items', verbose_name=_('produk'))
    quantity = models.PositiveIntegerField(_('jumlah'))
    unit_price = models.DecimalField(_('harga satuan'), max_digits=10, decimal_places=2)
    discount = models.DecimalField(_('diskon'), max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(_('total harga'), max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = _('item penjualan')
        verbose_name_plural = _('item penjualan')
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.unit}"
    
    def save(self, *args, **kwargs):
        self.total_price = (self.quantity * self.unit_price) - self.discount
        super().save(*args, **kwargs)
        
        # Update stock
        self.product.stock -= self.quantity
        self.product.save()

class StockAdjustment(models.Model):
    """Model untuk penyesuaian stok"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_adjustments', verbose_name=_('produk'))
    adjustment_type = models.CharField(
        _('tipe penyesuaian'),
        max_length=20,
        choices=[
            ('ADD', _('Tambah')),
            ('SUBTRACT', _('Kurang')),
        ]
    )
    quantity = models.PositiveIntegerField(_('jumlah'))
    reason = models.TextField(_('alasan'))
    adjusted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='stock_adjustments', verbose_name=_('disesuaikan oleh'))
    adjusted_at = models.DateTimeField(_('disesuaikan pada'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('penyesuaian stok')
        verbose_name_plural = _('penyesuaian stok')
        ordering = ['-adjusted_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.adjustment_type} {self.quantity}"
    
    def save(self, *args, **kwargs):
        if self.adjustment_type == 'ADD':
            self.product.stock += self.quantity
        else:
            self.product.stock -= self.quantity
        self.product.save()
        super().save(*args, **kwargs)
