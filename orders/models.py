from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Customer Model
class Customer(AbstractUser):
    username = None  # AbstractUser'dan gelen username'i devre dışı bırakıyoruz
    customer_name = models.CharField(max_length=100, unique=True)
    is_admin = models.BooleanField(default=False)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    customer_type = models.CharField(
        max_length=8,
        choices=[('Standard', 'Standard'), ('Premium', 'Premium')],
        default='Standard'
    )
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    USERNAME_FIELD = 'customer_name'

    def save(self, *args, **kwargs):
        # Şifre düz metinse, hashleyerek kaydet
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)

        # TotalSpent kontrolü ve customer_type güncellemesi
        if self.total_spent > 2000:
            self.customer_type = 'Premium'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.customer_name

# Product Model
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    stock = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.stock < 0:
            raise ValidationError("Stok miktarı sıfırdan küçük olamaz.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name

# Cart Model
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            Cart.objects.filter(customer=self.customer, is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart {self.id} for {self.customer.customer_name} ({'Active' if self.is_active else 'Inactive'})"

# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_name = models.CharField(max_length=255)
    product_image = models.URLField()

    def save(self, *args, **kwargs):
        self.price = self.product.price
        self.product_name = self.product.product_name
        if self.product.image:
            self.product_image = self.product.image.url
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} - {self.quantity}"

# Order Model
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )

    def waiting_time_seconds(self):
        current_time = timezone.now()
        if self.order_date:
            return (current_time - self.order_date).total_seconds()
        return None

    def clean(self):
        if self.quantity > 5:
            raise ValidationError('A customer can only order a maximum of 5 units of a product.')

    def __str__(self):
        return f"Order {self.order_id} by {self.customer.customer_name}"

# Log Model
class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    log_date = models.DateTimeField(auto_now_add=True)
    log_type = models.CharField(max_length=50)
    log_details = models.TextField()

    def __str__(self):
        return f"Log {self.log_id} for Order {self.order.order_id}"
