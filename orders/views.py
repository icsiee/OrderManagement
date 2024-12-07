from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Customer
from django.contrib.auth.hashers import make_password, check_password

# Kayıt (Register) fonksiyonu
def register(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        password = request.POST.get("password")
        budget = request.POST.get("budget")

        # Bilgileri kontrol et
        if not customer_name or not password or not budget:
            messages.error(request, "Tüm alanları doldurduğunuzdan emin olun.")
            return redirect('register')

        # Kullanıcı adı benzersiz mi kontrol et
        if Customer.objects.filter(customer_name=customer_name).exists():
            messages.error(request, "Bu kullanıcı adı zaten mevcut.")
            return redirect('register')

        try:
            # Bütçe aralığını kontrol et
            budget = float(budget)
            if budget < 500 or budget > 3000:
                messages.error(request, "Bütçe miktarı 500 ile 3000 TL arasında olmalıdır.")
                return redirect('register')

            # Yeni müşteri oluştur
            hashed_password = make_password(password)
            customer = Customer(
                customer_name=customer_name,
                password=hashed_password,
                budget=budget,
                total_spent=0
            )
            customer.save()

            # Başarı mesajını ayarla
            messages.success(request, "Kayıt başarılı! Giriş yapabilirsiniz.")
            return redirect('home')  # Ana sayfaya yönlendirme
        except Exception as e:
            messages.error(request, f"Kayıt sırasında bir hata oluştu: {str(e)}")
            return redirect('register')

    return render(request, 'register.html')

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
