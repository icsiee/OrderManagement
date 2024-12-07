from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Customer
from django.contrib.auth.hashers import make_password, check_password

# Kayıt (Register) fonksiyonu
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerRegistrationForm

def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Kayıt başarılı! Giriş yapabilirsiniz.")
            return redirect('home')  # Ana sayfaya yönlendirme
        else:
            messages.error(request, "Lütfen tüm alanları doğru şekilde doldurun.")
    else:
        form = CustomerRegistrationForm()

    return render(request, 'register.html', {'form': form})



# Giriş (Login) fonksiyonu
def login_view(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        password = request.POST.get("password")

        # Kullanıcıyı doğrulama
        try:
            customer = Customer.objects.get(customer_name=customer_name)
            if check_password(password, customer.password):  # Şifre doğrulama
                if not customer.is_admin:  # Sadece kullanıcılar için
                    login(request, customer)
                    messages.success(request, "Giriş başarılı!")
                    return redirect('home')  # Ana sayfaya yönlendirme
                else:
                    messages.error(request, "Admin kullanıcı için yanlış giriş bölümü.")
            else:
                messages.error(request, "Geçersiz şifre!")
        except Customer.DoesNotExist:
            messages.error(request, "Bu kullanıcı adı ile bir hesap bulunamadı.")

    return render(request, 'login.html')

# Admin Giriş (Login) fonksiyonu
def admin_login(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        password = request.POST.get("password")

        # Admini doğrulama
        try:
            admin = Customer.objects.get(customer_name=customer_name, is_admin=True)
            if check_password(password, admin.password):  # Şifre doğrulama
                login(request, admin)
                messages.success(request, "Admin girişi başarılı!")
                return redirect('admin_dashboard')  # Admin paneline yönlendirme
            else:
                messages.error(request, "Geçersiz şifre!")
        except Customer.DoesNotExist:
            messages.error(request, "Admin kullanıcı bulunamadı.")

    return render(request, 'login.html')

# Ana sayfa (Home) fonksiyonu
def home(request):
    return render(request, 'home.html')

# Admin paneli (Dashboard) fonksiyonu
def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        messages.error(request, "Bu sayfaya erişim izniniz yok!")
        return redirect('home')

    return render(request, 'admin_dashboard.html')

# Çıkış yapma fonksiyonu
def logout_view(request):
    logout(request)
    messages.success(request, "Başarıyla çıkış yaptınız!")
    return redirect('home')

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

