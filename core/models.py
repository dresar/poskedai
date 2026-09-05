from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Custom User model with email as the unique identifier."""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        OWNER = 'OWNER', _('Pemilik Toko')
        EMPLOYEE = 'EMPLOYEE', _('Karyawan')
    
    username = None
    email = models.EmailField(_('alamat email'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        verbose_name=_('peran')
    )
    phone_number = models.CharField(_('nomor telepon'), max_length=15, blank=True)
    address = models.TextField(_('alamat'), blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name=_('foto profil')
    )
    date_joined = models.DateTimeField(_('tanggal bergabung'), auto_now_add=True)
    last_login = models.DateTimeField(_('terakhir login'), auto_now=True)
    is_active = models.BooleanField(_('aktif'), default=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('pengguna')
        verbose_name_plural = _('pengguna')
        
    def __str__(self):
        return self.email
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_owner(self):
        return self.role == self.Role.OWNER
    
    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE
