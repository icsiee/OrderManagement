
from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import AbstractUser
from django.db import models
class Customer(AbstractUser):
    username = None  # AbstractUser'dan gelen username'ı devre dışı bırakıyoruz
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
        # Eğer şifre düz metinse, hashleyerek kaydet
        if not self.password.startswith('pbkdf2_'):  # Daha önce hashlenmemişse
            self.password = make_password(self.password)

        # TotalSpent kontrolü ve customer_type güncellemesi
        if self.total_spent > 2000:
            self.customer_type = 'Premium'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.customer_name



# Product model
# Product model
from django.core.exceptions import ValidationError
from django.db import models

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)  # Auto-generated unique ProductID
    product_name = models.CharField(max_length=100)  # ProductName
    stock = models.IntegerField()  # Available Stock
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product Price
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # Optional image
    def save(self, *args, **kwargs):
        try:
            self.stock = int(self.stock)  # Stok alanını int'e dönüştür
        except ValueError:
            raise ValidationError("Stok miktarı geçerli bir sayı olmalıdır.")

        if self.stock < 0:
            raise ValidationError("Stok miktarı sıfırdan küçük olamaz.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name



from django.db import models

# Cart model
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from django.db import models
from django.contrib.auth import get_user_model

Customer = get_user_model()

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Her müşteri birden fazla sepet oluşturabilir
    is_active = models.BooleanField(default=True)  # Sepetin aktif olup olmadığını belirler
    created_at = models.DateTimeField(auto_now_add=True)  # Sepetin oluşturulma tarihi
    updated_at = models.DateTimeField(auto_now=True)  # Sepetin son güncellenme tarihi

    def save(self, *args, **kwargs):
        """
        Save işlemi sırasında yalnızca bir aktif sepet olmasını sağlar.
        """
        if self.is_active:
            # Aynı müşteri için başka bir aktif sepeti pasif yap
            Cart.objects.filter(customer=self.customer, is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart {self.id} for {self.customer.customer_name} ({'Active' if self.is_active else 'Inactive'})"

    @staticmethod
    def get_or_create_active_cart(customer):
        """
        Müşteri için mevcut aktif sepeti döndürür. Aktif sepet yoksa yeni bir tane oluşturur.
        """
        cart = Cart.objects.filter(customer=customer, is_active=True).first()
        if not cart:
            cart = Cart.objects.create(customer=customer, is_active=True)
        return cart

    def complete_cart(self):
        """
        Sepeti tamamlar ve pasif hale getirir.
        """
        if self.is_active:
            self.is_active = False
            self.save()
        else:
            raise ValueError("Cart is already inactive.")


# CartItem model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Sepet ile ilişki
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Ürün ile ilişki
    quantity = models.PositiveIntegerField(default=1)  # Sepetteki ürün miktarı
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Fiyat alanı, ürün fiyatından alınacak
    product_name = models.CharField(max_length=255)  # Ürün adı
    product_image = models.URLField()  # Ürün görseli URL'si

    def save(self, *args, **kwargs):
        # Fiyat, ürünün fiyatından alınıyor
        if not self.price:
            self.price = self.product.price
        if not self.product_name:
            self.product_name = self.product.product_name
        if not self.product_image and self.product.image:
            self.product_image = self.product.image.url  # Görsel URL'sini al
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} - {self.quantity}"



# Order model
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)  # Auto-generated unique OrderID
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Foreign Key linking to Customer
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign Key linking to Product
    quantity = models.IntegerField()  # Quantity of the product ordered
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Total price for the order (quantity * price)
    order_date = models.DateTimeField(auto_now_add=True)  # Order date
    order_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        default='Pending'  # Default status is 'Pending'
    )

    # Ensure a customer can order a maximum of 5 units of a product
    def clean(self):
        if self.quantity > 5:
            raise ValidationError('A customer can only order a maximum of 5 units of a product.')

    def __str__(self):
        return f"Order {self.order_id} by {self.customer.customer_name}"

    def process_cart_to_order(self):
        # Aktif sepeti bul
        cart = Cart.objects.get(customer=self.customer, is_active=True)

        # Sepetteki ürünleri al
        cart_items = CartItem.objects.filter(cart=cart)

        for cart_item in cart_items:
            # Sipariş oluştur
            Order.objects.create(
                customer=self.customer,
                product=cart_item.product,
                quantity=cart_item.quantity,
                total_price=cart_item.quantity * cart_item.price,
            )

        # Sepet sıfırlanıyor
        cart.is_active = False
        cart.save()

        # Sepet içeriğini temizle
        cart_items.delete()


# Log model
class Log(models.Model):
    log_id = models.AutoField(primary_key=True)  # Auto-generated unique LogID
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Foreign Key linking to Customer
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # Foreign Key linking to Order
    log_date = models.DateTimeField(auto_now_add=True)  # Log date
    log_type = models.CharField(max_length=50)  # Type of log (e.g., 'Order Created', 'Order Cancelled')
    log_details = models.TextField()  # Details of the log

    def __str__(self):
        return f"Log {self.log_id} for Order {self.order.order_id}"

