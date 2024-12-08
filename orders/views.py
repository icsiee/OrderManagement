from django.views.decorators.csrf import csrf_exempt

from .forms import RegisterForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Kullanıcıyı kaydet
            messages.success(request, "Kayıt başarılı! Giriş yapabilirsiniz.")
            return redirect('login')  # Giriş sayfasına yönlendir
        else:
            messages.error(request, "Lütfen tüm alanları doğru şekilde doldurduğunuzdan emin olun.")
    else:
        form = RegisterForm()

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
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Customer
from django.contrib.auth.hashers import check_password


@csrf_exempt

# Kullanıcı Girişi (Customer Login)
def customer_login(request):
    customer_messages = []  # Müşteri girişine özel mesajlar
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        password = request.POST.get("password")

        try:
            customer = Customer.objects.get(customer_name=customer_name)

            if customer.is_admin:  # Admin müşteri girişine izin verilmez
                customer_messages.append("Admin kullanıcı müşteri formunu kullanamaz.")
            elif check_password(password, customer.password):
                login(request, customer)
                messages.success(request, "Müşteri girişi başarılı!")
                return redirect('customer_dashboard')
            else:
                customer_messages.append("Şifre hatalı.")
        except Customer.DoesNotExist:
            customer_messages.append("Böyle bir müşteri bulunamadı.")

    return render(request, 'registration/login.html', {'customer_messages': customer_messages})



# Admin Girişi (Admin Login)


from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Customer
from django.contrib.auth.hashers import check_password


@csrf_exempt
def admin_login(request):
    admin_messages = []  # Admin girişine özel mesajlar
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        password = request.POST.get("password")

        try:
            admin = Customer.objects.get(customer_name=customer_name)

            if not admin.is_admin:  # Müşteri admin formunu kullanamaz
                admin_messages.append("Müşteri hesabıyla admin girişi yapamazsınız.")
            elif check_password(password, admin.password):
                login(request, admin)

                # İlk defa giriş yapıldığını işaretle
                request.session['admin_logged_in'] = True
                return redirect('admin_dashboard')
            else:
                admin_messages.append("Şifre hatalı.")
        except Customer.DoesNotExist:
            admin_messages.append("Böyle bir admin bulunamadı.")

    return render(request, 'registration/login.html', {'admin_messages': admin_messages})




from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required
def customer_dashboard(request):
    customer_name = request.user.customer_name  # Giriş yapan müşterinin adı
    return render(request, 'customer_dashboard.html', {'customer_name': customer_name})


from django.shortcuts import render
from .models import Customer
@login_required
def admin_dashboard(request):
    # Superuser olmayan müşterileri filtrele
    customers = Customer.objects.filter(is_admin=False)

    # Eğer admin ilk kez giriş yaptıysa, başarı mesajını göster
    if request.session.get('admin_logged_in', False):
        messages.success(request, "Admin girişi başarılı!")
        # Admin'in ilk kez giriş yaptığını sıfırla
        request.session['admin_logged_in'] = False

    return render(request, 'admin_dashboard.html', {'customers': customers})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer
from .forms import CustomerForm


def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)  # İlgili müşteriyi al
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # Düzenleme sonrası admin sayfasına yönlendir
    else:
        form = CustomerForm(instance=customer)  # Mevcut müşteri verilerini forma ekle

    return render(request, 'edit_customer.html', {'form': form})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Customer

def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if not customer.is_admin:  # Admin kullanıcıların silinmesini engelle
        customer.delete()
        messages.success(request, "Müşteri başarıyla silindi.")
    else:
        messages.error(request, "Admin kullanıcıyı silemezsiniz.")
    return redirect('admin_dashboard')  # Admin paneline geri dön

from .forms import CustomerRegistrationForm

def add_customer(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Yeni müşteri başarıyla eklendi.")
            return redirect('admin_dashboard')  # Admin paneline geri dön
    else:
        form = CustomerRegistrationForm()

    return render(request, 'add_customer.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)  # Oturumu sonlandır
    return redirect('home')  # Çıkış yaptıktan sonra anasayfaya yönlendir



