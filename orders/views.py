from django.views.decorators.csrf import csrf_exempt
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



from django.contrib.auth import login
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
    customer_name = request.user.customer_name  # Giriş yapan kullanıcının adı (Customer modelinden alıyoruz)
    products = Product.objects.all()  # Stoktaki tüm ürünleri alıyoruz

    # Sepet kontrolü ve sepet bilgilerini kullanıcıya sağlama
    customer = request.user  # Kullanıcıyı doğrudan alıyoruz
    cart, created = Cart.objects.get_or_create(customer=customer, is_active=True)  # Kullanıcı için aktif sepeti al

    return render(request, 'customer_dashboard.html', {
        'customer_name': customer_name,
        'customer_balance': customer.budget,  # Bakiye bilgisi

        'products': products,  # Ürünler listelenecek
        'cart': cart,  # Kullanıcının aktif sepeti
    })


from django.contrib.auth.decorators import login_required
from .models import Log

from django.utils.timezone import now

def admin_dashboard(request):
    # Tüm siparişleri al
    orders = Order.objects.filter(order_status='Pending')

    logs=Log.objects.all()
    # Sipariş detaylarını işlemek için bir liste oluştur
    order_list = []
    for order in orders:
        # Bekleme süresini hesapla (örneğin, sipariş oluşturulma tarihinden itibaren geçen süre)
        waiting_time_seconds = (now() - order.order_date).total_seconds()

        # Müşteri türüne göre öncelik tabanı belirle
        priority_base = 15 if order.customer.customer_type == 'Premium' else 10

        # Öncelik skoru hesapla
        priority_score = priority_base + (waiting_time_seconds / 60 * 0.5)  # Dakika başına 0.5 artış

        # Siparişi listeye ekle
        order_list.append({
            'order_id': order.order_id,
            'customer': order.customer,
            'product': order.product,
            'quantity': order.quantity,
            'total_price': order.total_price,
            'waiting_time_display': int(waiting_time_seconds),  # Saniye olarak göster
            'priority_score': priority_score,
            'priority_base': priority_base,  # Burada priority_base'i de ekliyoruz
            'order_status': order.order_status,
        })

    # Siparişleri sıralama: Önce Premium kullanıcılar, ardından sırasıyla öncelik skoruna göre
    order_list = sorted(order_list, key=lambda x: (x['customer'].customer_type != 'Premium', -x['priority_score']))

    # Tüm müşterileri al
    customers = Customer.objects.all()
    logs = Log.objects.all()  # Tüm log kayıtlarını getir

    # Tüm ürünleri al
    products = Product.objects.all()

    # Şablona verileri gönder
    context = {
        'orders': order_list,
        'customers': customers,
        'products': products,
        'logs': logs,

    }
    return render(request, 'admin_dashboard.html', context)


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

def logout_view(request):
    logout(request)  # Oturumu sonlandır
    return redirect('home')  # Çıkış yaptıktan sonra anasayfaya yönlendir


# Random Müşteri Üretme Fonksiyonu
from django.contrib.auth.hashers import make_password
from faker import Faker

def generate_random_customers(request):
    fake = Faker()
    num_customers = random.randint(5, 10)  # 5-10 arasında rastgele müşteri sayısı
    new_customers = []

    # Premium kullanıcıları rastgele seçmek için bu listeyi oluşturuyoruz
    premium_count = 0
    minimum_premium = 2  # En az 2 premium kullanıcı olmalı

    for _ in range(num_customers):
        customer_name = fake.user_name()
        budget = random.uniform(500, 3000)  # 500 ile 3000 arasında rastgele bütçe
        total_spent = 0  # Toplam harcama her zaman 0 olacak

        # Eğer premium sayısı en az 2 değilse, premium yap
        if premium_count < minimum_premium:
            customer_type = 'Premium'
            premium_count += 1
        else:
            # Eğer premium sayısı 2 veya daha fazlaysa, rastgele premium ya da standard seç
            customer_type = 'Premium' if random.choice([True, False]) else 'Standard'

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


from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        # Validate input
        if not product_id or not quantity:
            return HttpResponse("Eksik veri gönderildi.", status=400)

        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return HttpResponse("Ürün bulunamadı.", status=404)

        # Check stock availability
        if product.stock < int(quantity):
            messages.error(request, f"{product.product_name} stokta yetersiz. Maksimum {product.stock} adet ekleyebilirsiniz.")
            return redirect('customer_dashboard')

        # Get or create the active cart
        cart, created = Cart.objects.get_or_create(customer=request.user, is_active=True)

        # Get or create the cart item
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            new_quantity = cart_item.quantity + int(quantity)
            if new_quantity > 5 or new_quantity > product.stock:
                messages.error(request, f"{product.product_name} için en fazla {min(5, product.stock)} adet sipariş verebilirsiniz.")
                return redirect('customer_dashboard')
            cart_item.quantity = new_quantity
        else:
            cart_item.quantity = min(int(quantity), product.stock, 5)

        # Save the updated cart item
        cart_item.save()

        # Success message
        messages.success(request, f"{product.product_name} başarıyla sepete eklendi.")
        return redirect('customer_dashboard')

from django.contrib.auth.decorators import login_required


@login_required
def view_cart(request):
    try:
        # Kullanıcının aktif sepetini al
        cart = Cart.objects.get(customer=request.user, is_active=True)
        cart_items = CartItem.objects.filter(cart=cart)

        # Toplam sepet tutarını hesapla
        total_price = sum(item.quantity * item.price for item in cart_items)

        # Kullanıcının bütçesini al
        user_budget = request.user.budget
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0
        user_budget = request.user.budget

    # Template'e verileri gönder
    return render(request, 'view_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'user_budget': user_budget
    })

from django.contrib.auth.decorators import login_required

# Sepet öğesi miktarını güncelleme
# views.py
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import CartItem

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import CartItem

def update_cart_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id)
        new_quantity = int(request.POST.get('quantity'))

        item.quantity = new_quantity
        item.save()

        # Sepet sayfasına yönlendir
        return redirect('view_cart')

# remove_cart_item, checkout gibi diğer view'lar zaten uygun şekilde çalışacaktır.


# Sepet öğesini silme
@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user, cart__is_active=True)
    cart_item.delete()

    return redirect('view_cart')


from datetime import datetime, timezone

from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):
    try:
        # Kullanıcının aktif sepetini getir
        cart = Cart.objects.get(customer=request.user, is_active=True)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        messages.error(request, "Aktif bir sepet bulunamadı. Sepet oluşturun.")
        return redirect('view_cart')  # Sepet sayfasına yönlendirme

    # Sepet boşsa işlem yapılamaz
    if not cart_items:
        messages.error(request, "Sepetinizde ürün bulunmuyor.")
        return redirect('view_cart')

    # 15 saniye kontrolü (örnek)
    request.session['checkout_start_time'] = datetime.now().timestamp()
    current_time = datetime.now().timestamp()
    start_time = request.session.get('checkout_start_time', current_time)
    if (current_time - start_time) > 10:
        messages.error(request, "Sipariş süresi doldu. Lütfen tekrar deneyin.")
        return redirect('view_cart')

    return render(request, 'checkout.html', {'cart_items': cart_items, "cart": cart})


from .models import Cart, CartItem, Order

from django.contrib.auth.decorators import login_required
from django.db import transaction
from datetime import datetime
from django.contrib import messages
from .models import Cart, CartItem, Order, Log
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def order_checkout(request):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(customer=request.user, is_active=True)
            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items:
                messages.error(request, "Sepetinizde ürün bulunmuyor.")
                return redirect('view_cart')

            # Calculate total price
            total_price = sum(item.quantity * item.price for item in cart_items)

            # Check customer budget
            if request.user.budget < total_price:
                messages.error(request, "Bütçeniz yetersiz.")
                return redirect('view_cart')

            with transaction.atomic():
                for item in cart_items:
                    # Check stock again for safety
                    if item.product.stock < item.quantity:
                        messages.error(request, f"{item.product.product_name} stokta yetersiz.")
                        return redirect('view_cart')

                    # Deduct stock and create the order
                    item.product.stock -= item.quantity
                    item.product.save()
                    Order.objects.create(
                        customer=request.user,
                        product=item.product,
                        quantity=item.quantity,
                        total_price=item.quantity * item.price,
                        order_status='Pending'
                    )

                # Deduct from customer budget
                request.user.budget -= total_price
                request.user.save()

                # Deactivate the cart
                cart.is_active = False
                cart.save()

            messages.success(request, "Siparişiniz başarıyla oluşturuldu!")
            return redirect('customer_dashboard')

        except Cart.DoesNotExist:
            messages.error(request, "Aktif bir sepet bulunamadı.")
            return redirect('view_cart')

    return redirect('checkout')


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
    default_image_path = "product_images/kahvaltilik_krep.jpg"

    # Ürünleri ekleyin veya stokları güncelleyin
    for product_data in default_products:
        product, created = Product.objects.get_or_create(
            product_name=product_data["product_name"],
            defaults={
                "stock": product_data["stock"],
                "price": product_data["price"],
                "image": default_image_path,
            },
        )

        if created:
            messages.success(request, f"{product.product_name} başarıyla eklendi.")
        else:
            # Ürün varsa, stok miktarını güncelleyin
            if product.stock != product_data["stock"]:
                old_stock = product.stock
                product.stock = product_data["stock"]
                product.save()
                messages.info(request, f"{product.product_name} stok miktarı {old_stock} → {product_data['stock']} olarak güncellendi.")
            else:
                messages.warning(request, f"{product.product_name} zaten mevcut ve stok miktarı güncellenmedi.")

    messages.success(request, "Sabit ürünler başarıyla eklendi ve güncellendi!")
    return redirect("admin_dashboard")  # Admin dashboard'unuzun URL ismini yazın


def delete_all_products(request):
    # Veritabanındaki tüm ürünleri sil
    Product.objects.all().delete()

    # Başarı mesajı
    messages.success(request, "Tüm ürünler başarıyla silindi.")
    return redirect("admin_dashboard")  # Admin dashboard'unuzun URL ismini yazın


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product


def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        try:
            product_name = request.POST.get('product_name')
            stock = int(request.POST.get('stock'))
            price = float(request.POST.get('price'))
            image = request.FILES.get('image')

            # Ürün bilgilerini güncelle
            product.product_name = product_name
            product.stock = stock
            product.price = price
            if image:
                product.image = image

            product.save()
            messages.success(request, f"{product.product_name} başarıyla güncellendi.")
            return redirect('admin_dashboard')

        except ValueError:
            messages.error(request, "Lütfen geçerli bir stok ve fiyat değeri girin.")
        except Exception as e:
            messages.error(request, f"Güncelleme sırasında bir hata oluştu: {e}")

    # Sadece edit_product.html için mesaj gönder
    if request.method == 'GET':  # Sadece sayfa açılırken bu mesaj gönderilsin
        messages.info(request, "Diğer işlemler beklemeye alındı.")

    return render(request, 'edit_product.html', {'product': product})


def all_orders(request):
    orders = Order.objects.all()  # Veritabanındaki tüm siparişleri al
    context = {
        'orders': orders,
    }
    return render(request, 'all_orders.html', context)


def order_detail(request, order_id):
    # Siparişi ID'sine göre al
    order = get_object_or_404(Order, order_id=order_id)

    # Siparişin detaylarını şablona gönder
    context = {
        'order': order,
    }
    return render(request, 'order_detail.html', context)


from django.contrib.auth.decorators import login_required

@login_required
def delete_order(request, order_id):
    from .models import Order, Customer, Product  # Gerekli modelleri içe aktarın

    # Siparişi bulun
    order = get_object_or_404(Order, order_id=order_id)

    # Transaction kullanarak güvenli bir silme işlemi
    with transaction.atomic():
        # Siparişi sil
        order.delete()

    # Mesaj göster
    messages.success(request, f"Sipariş ID {order_id} başarıyla silindi.")

    # Admin paneline yönlendir
    return redirect('admin_dashboard')


from .forms import ProductForm

def purchase_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    customer = get_object_or_404(Customer, id=1)  # Örnek, sabit bir müşteri
    requested_quantity = 5  # Örnek

    # Basit bir stoğa bakma kontrolü:
    if product.stock < requested_quantity:
        # Log kaydı oluştur
        Log.objects.create(
            customer_id=customer.id,
            log_type='Hata',
            customer_type=customer.customer_type,
            product_name=product.product_name,
            quantity=requested_quantity,
            result='Ürün stoğu yetersiz'
        )
        messages.error(request, "Stok yetersiz olduğu için satın alma başarısız.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla güncellendi!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Geçersiz veri girdiniz.')

    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})


from django.views.decorators.csrf import csrf_exempt

from orders.models import Order, Log, Product, Customer


@csrf_exempt
def process_order(request, order_id):
    try:
        # Siparişi alın
        order = Order.objects.select_related('customer', 'product').get(order_id=order_id)

        # Eğer siparişin durumu 'Completed' değilse, 'Cancelled' olarak güncelle
        if order.order_status != 'Completed':
            order.order_status = 'Cancelled'
            order.save()

        customer = order.customer
        product = order.product
        quantity = order.quantity
        total_price = order.total_price

        # İşlemleri atomik bir blok içinde gerçekleştir (transaction.atomic)
        with transaction.atomic():
            # Veritabanından en güncel değerleri alın
            product.refresh_from_db()
            customer.refresh_from_db()

            # Stok kontrolü
            if product.stock < quantity:
                order.order_status = 'Cancelled'
                result = "Stok Yetersiz"
            # Bütçe kontrolü
            elif customer.budget < total_price:
                order.order_status = 'Cancelled'
                result = "Bütçe Yetersiz"
            else:
                # Siparişi tamamlama
                product.stock -= quantity
                customer.budget -= total_price
                customer.total_spent += total_price
                order.order_status = 'Completed'
                result = "Sipariş Tamamlandı"

                # Değişiklikleri kaydet
                product.save()
                customer.save()
                order.save()

        # Log kaydı
        Log.objects.create(
            customer_id=customer.id,
            log_type='Bilgilendirme',
            customer_type=customer.customer_type,
            product=product.product_name,
            quantity=quantity,
            transaction_result=result
        )

        return JsonResponse({'status': order.order_status, 'result': result})

    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        # Beklenmedik bir hata durumunda detayları logla ve döndür
        print(f"Unexpected Error: {e}")
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)



from django.db import transaction

def complete_order(request, order_id):
    # Parametreleri al
    quantity = request.GET.get('quantity')
    product_id = request.GET.get('product_id')

    # Eğer quantity veya product_id geçerli değilse, hata dön
    if quantity is None or product_id is None or not quantity.isdigit():
        return JsonResponse({'message': 'Geçersiz parametreler.'}, status=400)

    quantity = int(quantity)
    product = get_object_or_404(Product, product_id=product_id)  # Ürün ID ile ürünü al
    order = get_object_or_404(Order, order_id=order_id)  # Sipariş ID ile siparişi al
    customer = order.customer  # Siparişi veren müşteri

    # Stok kontrolü ve bütçe işlemleri
    if product.stock >= quantity:  # Stok yeterli mi?
        if customer.budget >= order.total_price:  # Bütçe yeterli mi?
            # Sipariş işlemleri
            with transaction.atomic():  # Veritabanı işlemleri atomik olarak yapılacak
                product.stock -= quantity  # Stoktan sipariş edilen miktar düşülür
                product.save()  # Ürün güncellenir
                customer.budget -= order.total_price  # Müşterinin bütçesinden sipariş tutarı düşülür
                customer.save()  # Müşteri kaydı güncellenir
                order.order_status = 'Completed'  # Sipariş durumu "Tamamlandı" olarak güncellenir
                order.save()  # Sipariş kaydı güncellenir
                return JsonResponse({'message': 'Sipariş başarıyla tamamlandı, stok ve bütçe güncellendi.'})
        else:
            order.order_status = 'Cancelled'  # Bütçe yetersizse sipariş iptal edilir
            order.save()
            return JsonResponse({'message': 'Bütçe yetersiz, sipariş iptal edildi.'})
    else:
        order.order_status = 'Cancelled'  # Stok yetersizse sipariş iptal edilir
        order.save()
        return JsonResponse({'message': 'Stok yetersiz, sipariş iptal edildi.'})

@login_required
def completed_orders(request):
    orders = Order.objects.select_related('customer', 'product').filter(order_status='Completed')
    for order in orders:
        print(order.customer.customer_name)  # Burada müşteri adını kontrol edebilirsiniz.
    return render(request, 'completed_orders.html', {'orders': orders})


@login_required
def cancelled_orders(request):
    orders = Order.objects.filter(order_status='Cancelled')
    return render(request, 'cancelled_orders.html', {'orders': orders})


def get_pending_orders(request):
    # Sadece "Pending" siparişleri alıyoruz ve gerekli verileri JSON formatında döndürüyoruz
    pending_orders = Order.objects.filter(order_status='Pending').values(
        'order_id', 'customer__customer_name', 'product__product_name', 'quantity', 'total_price', 'order_date', 'order_status'
    )
    orders_list = list(pending_orders)  # QuerySet'i listeye çeviriyoruz
    return JsonResponse({'orders': orders_list})

from django.shortcuts import render, redirect

from datetime import datetime

import random
from django.utils import timezone  # Doğru timezone kütüphanesi
from django.contrib import messages
from django.shortcuts import redirect
from .models import Order, Product, Customer

def create_random_orders(request):
    # Veritabanından tüm müşterileri ve ürünleri al
    customers = Customer.objects.all()
    products = Product.objects.all()

    # Eğer müşteri veya ürün yoksa hata mesajı ver
    if not customers.exists():
        messages.error(request, "Rastgele sipariş oluşturmak için en az bir müşteri gereklidir.")
        return redirect('admin_dashboard')
    if not products.exists():
        messages.error(request, "Rastgele sipariş oluşturmak için en az bir ürün gereklidir.")
        return redirect('admin_dashboard')

    # Rastgele 20-30 sipariş oluştur
    num_orders = random.randint(20, 30)
    for _ in range(num_orders):
        # Rastgele bir müşteri ve ürün seç
        customer = random.choice(customers)
        product = random.choice(products)

        # Rastgele miktar belirle
        quantity = random.randint(1, 5)  # 1 ile 5 arasında miktar
        total_price = product.price * quantity

        # Sipariş oluştur
        Order.objects.create(
            customer=customer,
            product=product,
            quantity=quantity,
            total_price=total_price,
            order_date=timezone.now(),  # Hata burada düzeltiliyor
            order_status="Pending"  # Durumu "Pending" olarak ayarla
        )

    # Başarı mesajı ekle
    messages.success(request, f"{num_orders} adet rastgele sipariş başarıyla oluşturuldu.")
    return redirect('admin_dashboard')


from django.shortcuts import get_object_or_404
from .models import Order

def delete_pending_order(request, order_id):
    try:
        # Order'ı al
        order = get_object_or_404(Order, order_id=order_id)

        # Order'ın durumu 'Pending' mi kontrol et
        if order.order_status == 'Pending':
            order.delete()  # Silme işlemi

            return JsonResponse({
                'success': True,
                'message': 'Order deleted successfully.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Order is not in Pending status.'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


from django.http import JsonResponse
from .models import Customer

# views.py
from django.shortcuts import render
from .models import Log

# views.py
from django.shortcuts import render
from .models import Log

def log_panel(request):
    logs = Log.objects.all().order_by('-transaction_time')  # Logları zamana göre sırala (en yeni en üstte)
    return render(request, 'admin_dashboard.html', {'logs': logs})
