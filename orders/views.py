from django.http import HttpResponse
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
            # Kayıt başarılı mesajı
            messages.success(request, 'Kayıt başarılı! Giriş yapabilirsiniz.')

            # Kullanıcıyı home sayfasına yönlendir
            return redirect('home')
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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product, Cart

@csrf_exempt
@login_required
def customer_dashboard(request):
    customer_name = request.user.customer_name  # Giriş yapan kullanıcının adı (Customer modelinden alıyoruz)
    products = Product.objects.all()  # Stoktaki tüm ürünleri alıyoruz

    # Sepet kontrolü ve sepet bilgilerini kullanıcıya sağlama
    customer = request.user  # Kullanıcıyı doğrudan alıyoruz
    cart, created = Cart.objects.get_or_create(customer=customer, is_active=True)  # Kullanıcı için aktif sepeti al

    return render(request, 'customer_dashboard.html', {
        'customer_name': customer_name,
        'products': products,  # Ürünler listelenecek
        'cart': cart,  # Kullanıcının aktif sepeti
    })



from .models import Product

from django.shortcuts import render
from .models import Customer
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer, Product

@login_required
def admin_dashboard(request):
    # Superuser olmayan müşterileri filtrele
    customers = Customer.objects.filter(is_admin=False)
    products = Product.objects.all()  # Tüm ürünleri getir

    # Eğer admin ilk kez giriş yaptıysa, başarı mesajını göster
    if request.session.get('admin_logged_in', False):
        messages.success(request, "Admin girişi başarılı!")
        # Admin'in ilk kez giriş yaptığını sıfırla
        request.session['admin_logged_in'] = False

    # Veri sözlüğü sadece bir kez kullanılarak render yapılır
    return render(request, 'admin_dashboard.html', {'customers': customers, 'products': products})


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

# Tüm Kullanıcıları Silme View
def delete_all_customers(request):
    if request.user.is_superuser:  # Yalnızca superuser erişebilir
        # Superuser olmayan tüm müşterileri sil
        Customer.objects.filter(is_admin=False).delete()  # Superuser hariç tüm müşterileri sileriz

        # Başarılı bir mesaj göster
        messages.success(request, "Tüm müşteriler başarıyla silindi, superuser hariç.")
    else:
        # Eğer kullanıcı superuser değilse, erişim izni verilmez
        messages.error(request, "Bu işlem için yeterli izinleriniz yok.")

    return redirect('admin_dashboard')  # Admin dashboard'a geri yönlendir


# Ürün ekleme işlemi
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product

from django.shortcuts import redirect
from django.contrib import messages
from .models import Product

def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        image = request.FILES.get('image')  # Görsel yükleniyor

        try:
            stock = int(stock)
            price = float(price)
        except ValueError:
            messages.error(request, "Stok ve fiyat alanları geçerli sayılar olmalıdır.")
            return redirect('add_product')

        if stock < 0:
            messages.error(request, "Stok miktarı sıfırdan küçük olamaz.")
            return redirect('add_product')

        # image_url yerine 'image' alanını kullanın
        product = Product(
            product_name=product_name,
            stock=stock,
            price=price,
            image=image,  # image alanını kullanın
        )
        product.save()
        messages.success(request, "Ürün başarıyla eklendi.")
        return redirect('admin_dashboard')

    return redirect('admin_dashboard')



# Ürün silme işlemi
@login_required
def delete_product(request, product_id):
    if not request.user.is_admin:
        return redirect('home')  # Eğer kullanıcı admin değilse home sayfasına yönlendir

    try:
        product = Product.objects.get(product_id=product_id)
        product.delete()
        messages.success(request, f"{product.product_name} başarıyla silindi.")
    except Product.DoesNotExist:
        messages.error(request, "Ürün bulunamadı.")

    return redirect('admin_dashboard')


# Stok güncelleme işlemi
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages

@csrf_exempt
@login_required
def update_stock(request, product_id):
    if request.method == 'POST':
        # Formdan gelen stok bilgisini al
        new_stock = request.POST.get('new_stock')

        if not new_stock:
            # Boş veri kontrolü
            messages.error(request, "Yeni stok değeri boş olamaz.")
            return redirect('admin_dashboard')

        try:
            # Yeni stok değerini tam sayı olarak dönüştür
            new_stock = int(new_stock)

            # Ürünü al
            product = get_object_or_404(Product, product_id=product_id)

            # Stok değerini güncelle
            product.stock = new_stock
            product.save()

            # Başarılı mesajı ekle
            messages.success(request, f"{product.product_name} stok güncellendi!")
        except ValueError:
            # Sayıya dönüştürülemezse hata mesajı
            messages.error(request, "Geçerli bir stok değeri giriniz.")
        except Product.DoesNotExist:
            messages.error(request, "Ürün bulunamadı.")
        return redirect('admin_dashboard')
    else:
        return HttpResponse("Bu işlem sadece POST yöntemiyle yapılabilir.", status=405)


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Cart, CartItem


from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Product, Cart, CartItem

# Sepete ürün eklemek için view fonksiyonu
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        # Girdi doğrulaması
        if not product_id or not quantity:
            return HttpResponse("Eksik veri gönderildi.", status=400)

        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return HttpResponse("Ürün bulunamadı.", status=404)

        # Stoktaki miktarı kontrol et
        if int(quantity) > product.stock:
            messages.error(request, f"{product.product_name} için yeterli stok bulunmamaktadır.")
            return redirect('customer_dashboard')

        # Sepeti oluştur veya aktif sepeti al
        cart, created = Cart.objects.get_or_create(customer=request.user, is_active=True)

        # Sepet öğesini kontrol et veya oluştur
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            # Mevcut miktarı artırmadan önce, toplam miktarın 5'i geçmediğini kontrol et
            new_quantity = cart_item.quantity + int(quantity)
            if new_quantity > 5:
                # Hata mesajı ekle ve sepete eklemeyi yapma
                messages.error(request, f"{product.product_name} için en fazla 5 adet sipariş verebilirsiniz.")
                return redirect('customer_dashboard')
            cart_item.quantity = new_quantity
        else:
            # Yeni miktarı belirle
            cart_item.quantity = int(quantity)

        # Maksimum 5 ürün limiti
        cart_item.quantity = min(cart_item.quantity, 5)

        # Gerekli alanları doldur
        cart_item.save()  # Veritabanına kaydet

        # Başarı mesajı
        messages.success(request, f"{product.product_name} başarıyla sepete eklendi.")

        return redirect('customer_dashboard')  # Sepet sayfasına yönlendir




@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(customer=request.user, is_active=True)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        cart_items = []

    return render(request, 'view_cart.html', {'cart_items': cart_items})

from django.shortcuts import get_object_or_404, redirect
from .models import CartItem

# Sepet öğesi miktarını güncelleme
from django.shortcuts import get_object_or_404, redirect
from .models import CartItem
from django.contrib.auth.decorators import login_required

# Sepet öğesi miktarını güncelleme
@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user, cart__is_active=True)
        new_quantity = int(request.POST.get('quantity', 1))

        # Maksimum 5 ürün limiti
        cart_item.quantity = min(new_quantity, 5)
        cart_item.save()

        return redirect('view_cart')

# Sepet öğesini silme
@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user, cart__is_active=True)
    cart_item.delete()

    return redirect('view_cart')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem

@login_required
def checkout(request):
    try:
        # Aktif sepeti al
        cart = Cart.objects.get(customer=request.user, is_active=True)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        cart_items = []

    # Sepet boşsa, checkout'a gitmeyi engelle
    if not cart_items:
        return redirect('view_cart')  # Sepet boşsa, sepete yönlendir

    return render(request, 'checkout.html', {'cart_items': cart_items,"cart":cart})



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cart, CartItem

def order_checkout(request):
    if request.method == 'POST':
        try:
            # Kullanıcının aktif sepetini al
            cart_id = request.POST.get('cart_id')
            cart=Cart.objects.filter(id=cart_id).first()
            cart_items = CartItem.objects.filter(cart_id=cart_id)

            # Stok güncellemesi yap
            for item in cart_items:
                product = item.product
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save()
                else:
                    messages.error(request, f"{product.product_name} stoğu yetersiz.")
                    return redirect('checkout')  # Yetersiz stok varsa tekrar checkout sayfasına dön

            # Siparişi tamamlandı olarak işaretle
            cart.is_active = False
            cart.save()

            # Başarılı mesaj ekle
            messages.success(request, "Sipariş onaylandı!")

            # Yönlendirme yap
            return redirect('customer_dashboard')
        except Cart.DoesNotExist:
            messages.error(request, "Aktif bir sepet bulunamadı.")
            return redirect('checkout')
        return redirect('checkout')
    else:
        print("ezgi")
        # GET isteği için checkout sayfasına dön
        return redirect('checkout')


from django.shortcuts import redirect
from django.contrib import messages
from .models import Product


def add_default_products(request):
    # Sabit ürünler
    default_products = [
        {"product_name": "Product1", "stock": 500, "price": 100},
        {"product_name": "Product2", "stock": 10, "price": 50},
        {"product_name": "Product3", "stock": 200, "price": 45},
        {"product_name": "Product4", "stock": 75, "price": 75},
        {"product_name": "Product5", "stock": 0, "price": 500},
    ]

    # Media klasöründeki varsayılan görselin yolu
    default_image_path = "media/kahvaltilik_krep.jpg"

    # Ürünleri ekleyin
    for product_data in default_products:
        product, created = Product.objects.get_or_create(
            product_name=product_data["product_name"],
            defaults={
                "stock": product_data["stock"],
                "price": product_data["price"],
                "image": default_image_path,
            },
        )
        if not created:
            messages.warning(request, f"{product.product_name} zaten mevcut.")

    messages.success(request, "Sabit ürünler başarıyla eklendi!")
    return redirect("admin_dashboard")  # Admin dashboard'unuzun URL ismini yazın

