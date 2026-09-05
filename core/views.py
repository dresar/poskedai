from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User
from inventory.models import Product, Sale, Purchase

# Forms will be defined here or imported from forms.py
from django import forms

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

def login_view(request):
    """View function for user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, _('Email atau password salah. Silakan coba lagi.'))
    
    return render(request, 'core/login.html')

def logout_view(request):
    """View function for user logout"""
    logout(request)
    messages.success(request, _('Anda telah berhasil logout.'))
    return redirect('login')

@login_required
def dashboard(request):
    """View function for the dashboard"""
    # Get counts for dashboard stats
    from django.db.models import F
    low_stock_count = Product.objects.filter(stock__lte=F('min_stock')).count()
    total_products = Product.objects.count()
    
    # Different dashboard views based on user role
    context = {
        'low_stock_count': low_stock_count,
        'total_products': total_products,
    }
    
    if request.user.is_admin or request.user.is_owner:
        # Add more stats for admin/owner
        recent_sales = Sale.objects.order_by('-sale_date')[:5]
        recent_purchases = Purchase.objects.order_by('-purchase_date')[:5]
        
        # Calculate total sales and purchases for current month
        from django.utils import timezone
        from django.db.models import Sum
        import datetime
        
        today = timezone.now()
        month_start = datetime.date(today.year, today.month, 1)
        
        monthly_sales = Sale.objects.filter(sale_date__gte=month_start).aggregate(Sum('grand_total'))
        monthly_purchases = Purchase.objects.filter(purchase_date__gte=month_start).aggregate(Sum('total_amount'))
        
        context.update({
            'recent_sales': recent_sales,
            'recent_purchases': recent_purchases,
            'monthly_sales': monthly_sales['grand_total__sum'] or 0,
            'monthly_purchases': monthly_purchases['total_amount__sum'] or 0,
        })
    
    return render(request, 'core/dashboard.html', context)

@login_required
def profile(request):
    """View function for viewing user profile"""
    return render(request, 'core/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    """View function for editing user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profil Anda telah berhasil diperbarui.'))
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/edit_profile.html', {'form': form})
        
@login_required
def change_password(request):
    """View function for changing user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, _('Password Anda telah berhasil diubah.'))
            return redirect('core:profile')
        else:
            messages.error(request, _('Silakan perbaiki kesalahan di bawah ini.'))
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/change_password.html', {'form': form})

@login_required
def change_password(request):
    """View function for changing password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, _('Password Anda telah berhasil diperbarui.'))
            return redirect('core:profile')
        else:
            messages.error(request, _('Silakan perbaiki kesalahan di bawah ini.'))
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/change_password.html', {'form': form})
