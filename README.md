# EŞ Zamanlı Sipariş ve Stok Yönetimi Uygulaması

Bu proje, birden fazla kullanıcının eş zamanlı olarak sipariş ve stok yönetimini yürüttüğü bir sistem tasarlamaya yönelik bir uygulamayı ele alır. Sistem, multithreading ve senkronizasyon mekanizmaları kullanarak aynı kaynağa eş zamanlı erişim problemlerini çözmeyi hedefler.

## Proje Hakkında

**Amaç:** 

Bu projede bir sipariş ve stok yönetim sistemi geliştirilmiştir. Premium ve Standart müşterilerin dinamik önceliklerle çalıştığı, admin panelinin stok kontrolü ve güncelleme yaptığı bir platform sunulmaktadır.

**Programlama Dilleri:** Python (Django Framework)

**Veritabanı:** MySQL

**UI:** Bootstrap ve jQuery ile desteklenmiş bir web arayüzü

## Özellikler

1. **Müşteri Yönetimi:**
   - Premium ve Standart müşteri tipi desteklenir.
   - Müşteri başına maksimum 5 adet stok siparişi bulunur.
   - Dinamik öncelik skoru hesaplaması.

2. **Stok Yönetimi:**
   - 5 farklı ürün sabit stok ve fiyat değerleriyle başlatılır.
   - Admin ürün ekleyebilir, silebilir ve stok miktarını güncelleyebilir.

3. **Sipariş Yönetimi:**
   - Ürün stoğu ve müşteri bakiyesi kontrol edilir.
   - İşlem başarısız olduğunda hata mesajları loglanır.

4. **Dinamik Öncelik Sistemi:**
   - Premium müşteriler önceliklidir.
   - Standart müşteriler bekleme sürelerine göre sıralanır.

5. **Gerçek Zamanlı Loglama:**
   - Tüm işlemler loglanır.
   - Log tipi, hata mesajları ve işlem detayları takip edilir.

## Kurulum ve Kullanım

### Gereksinimler
- Python 3.8+
- Django 4.2+
- MySQL
- pip (Python Paket Yöneticisi)

### Kurulum

1. **Depoyu Klonlayın:**
   ```bash
   git clone https://github.com/kullanici_adi/order_management.git
   cd order_management
   ```

2. **Gereksinimleri Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Veritabanı Ayarlarını Yapın:**
   `settings.py` dosyasındaki veritabanı ayarlarınızı MySQL bilgilerinizle güncelleyin.

4. **Veritabanını Oluşturun:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Yönetici Kullanıcısı Oluşturun:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Sunucuyu Başlatın:**
   ```bash
   python manage.py runserver
   ```

### Kullanım
- **Admin Paneli:** `http://127.0.0.1:8000/admin` adresinden ulaşılabilir.
- **Müşteri Paneli:** Müşteriler siparişlerini bu panelden yönetebilir.
- **Loglar:** Tüm log bilgileri gerçek zamanlı olarak arayüzde gösterilir.

## Proje Yapısı
```
├── es-zamanli-siparis-yonetimi/
│   ├── orders/  # Ana uygulama
│   ├── templates/  # HTML dosyaları
│   ├── static/  # CSS ve JavaScript
│   ├── db.sqlite3  # Geliştirme için kullanılan SQLite
│   ├── manage.py
│   └── requirements.txt
├── README.md
```

## Katkılar
Katkıda bulunmak isterseniz lütfen bir **Pull Request** oluşturun. Önerilerinizi bekliyoruz!

## Lisans
Bu proje MIT Lisansı altında dağıtılmaktadır. Daha fazla bilgi için `LICENSE` dosyasını kontrol edebilirsiniz.
