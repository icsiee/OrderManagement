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


@csrf_exempt

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
                return redirect('customer_dashboard')  # Başarıyla giriş yaptıktan sonra customer_dashboard sayfasına yönlendir
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

import random
from faker import Faker
from django.contrib import messages
from django.shortcuts import redirect
from .models import Customer
from django.utils.crypto import get_random_string

# Random Müşteri Üretme Fonksiyonu
import random
from faker import Faker
from django.contrib import messages
from django.shortcuts import redirect
from .models import Customer

# Random Müşteri Üretme Fonksiyonu
import random
from faker import Faker
from django.contrib.auth.hashers import make_password  # make_password fonksiyonunu ekledik
from django.contrib import messages
from django.shortcuts import redirect
from .models import Customer

# Random Müşteri Üretme Fonksiyonu
def generate_random_customers(request):
    fake = Faker()
    num_customers = random.randint(5, 10)  # 5-10 arasında rastgele müşteri sayısı
    new_customers = []

    # Premium kullanıcıları rastgele seçmek için bu listeyi oluşturuyoruz
    premium_count = 0

    for _ in range(num_customers):
        customer_name = fake.user_name()
        budget = random.uniform(500, 3000)  # 500 ile 3000 arasında rastgele bütçe
        total_spent = 0  # Toplam harcama her zaman 0 olacak

        # Premium kullanıcıları rastgele seçiyoruz, en az 2 tane olmalı
        if premium_count < 2 and random.choice([True, False]):
            customer_type = 'Premium'
            premium_count += 1
        else:
            customer_type = 'Standard'

        # Şifreyi hashle
        hashed_password = make_password('1')  # Şifreyi hashliyoruz

        # Müşteriyi oluştur
        customer = Customer(
            customer_name=customer_name,
            password=hashed_password,  # Hashlenmiş şifreyi kaydediyoruz
            budget=round(budget, 2),
            total_spent=total_spent,  # Toplam harcama 0
            customer_type=customer_type
        )
        new_customers.append(customer)

    # Müşterileri veritabanına kaydet
    Customer.objects.bulk_create(new_customers)

    # Mesaj gönder
    messages.success(request, f"{num_customers} yeni müşteri başarıyla oluşturuldu.")
    return redirect('admin_dashboard')

from django.contrib import messages
from django.shortcuts import redirect
from .models import Customer

# Tüm Kullanıcıları Silme
def delete_all_customers(request):
    # Superuser olmayan tüm müşterileri sil
    Customer.objects.filter(is_admin=False).delete()  # Sadece admin olmayanları sileriz

    # Mesaj göster
    messages.success(request, "Tüm müşteriler başarıyla silindi, superuser hariç.")
    return redirect('admin_dashboard')  # Admin paneline geri dön




