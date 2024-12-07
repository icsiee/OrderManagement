from django.core.exceptions import ValidationError
from django.db import models


# Customer model (User model for register/login)
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class Customer(AbstractUser):
    # username alanı yerine customer_name kullanılır
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
        if self.total_spent > 2000:
            self.customer_type = 'Premium'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.customer_name




# Product model
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)  # Auto-generated unique ProductID
    product_name = models.CharField(max_length=100)  # ProductName
    stock = models.IntegerField()  # Available Stock
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product Price

    def __str__(self):
        return self.product_name


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


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from .models import Customer

# Customer login view
def customer_login(request):
    if request.method == "POST":
        customer_name = request.POST.get('customer_name')
        password = request.POST.get('password')

        try:
            # Check if the customer exists and is not an admin
            customer = Customer.objects.get(customer_name=customer_name)

            if customer.is_admin:
                messages.error(request, "Admin girişine izniniz yok.")
                return redirect('customer_login')

            # Check if the password is correct
            if check_password(password, customer.password):
                # Log the user in
                login(request, customer)
                return redirect('home')  # Redirect to the homepage or dashboard
            else:
                messages.error(request, "Şifre hatalı.")
                return redirect('customer_login')

        except Customer.DoesNotExist:
            messages.error(request, "Kullanıcı adı bulunamadı.")
            return redirect('customer_login')

    return render(request, 'customer_login.html')

# Admin login view
def admin_login(request):
    if request.method == "POST":
        customer_name = request.POST.get('customer_name')
        password = request.POST.get('password')

        try:
            # Check if the user exists and is an admin
            customer = Customer.objects.get(customer_name=customer_name)

            if not customer.is_admin:
                messages.error(request, "Customer girişine izniniz yok.")
                return redirect('admin_login')

            # Check if the password is correct
            if check_password(password, customer.password):
                # Log the user in
                login(request, customer)
                return redirect('admin_dashboard')  # Redirect to the admin dashboard
            else:
                messages.error(request, "Şifre hatalı.")
                return redirect('admin_login')

        except Customer.DoesNotExist:
            messages.error(request, "Kullanıcı adı bulunamadı.")
            return redirect('admin_login')

    return render(request, 'admin_login.html')


