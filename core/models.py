from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from io import BytesIO
from django.core.files import File
import barcode
from barcode.writer import ImageWriter
import qrcode


# ------------------ CONTEXT PROCESSORS ------------------
def navbar_context(request):
    return {
        'navbar_logo': NavbarLogo.objects.all(),
        'navbar_menu_items': NavbarMenuItem.objects.all()
    }


def site_settings(request):
    settings = SiteSettings.objects.first()
    return {'site_settings': settings}


# ------------------ SITE SETTINGS ------------------
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="The Floral Studio")
    logo = models.ImageField(upload_to="logo/")
    primary_color = models.CharField(max_length=20, default="#2e7d32")
    secondary_color = models.CharField(max_length=20, default="#ffffff")
    text_color = models.CharField(max_length=20, default="#000000")

    def __str__(self):
        return self.site_name


class NavbarLogo(models.Model):
    logo_image = models.ImageField(upload_to='navbar/logo/')

    def __str__(self):
        return "Navbar Logo"


class NavbarMenuItem(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.name


class NavLink(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class HeroSlide(models.Model):
    headline = models.CharField(max_length=200)
    subtext = models.TextField(blank=True, null=True)
    button_text = models.CharField(max_length=100, blank=True, null=True)
    button_link = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='hero_slides/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.headline


# ------------------ BARCODE SETTINGS ------------------
class BarcodeSettings(models.Model):
    BARCODE_TYPES = [
        ('code39', 'Code 39'),
        ('code128', 'Code 128'),
        ('ean13', 'EAN-13'),
        ('qrcode', 'QR Code'),
    ]
    barcode_type = models.CharField(max_length=20, choices=BARCODE_TYPES, default='code128')

    def __str__(self):
        return self.get_barcode_type_display()


# ------------------ PRODUCT MODELS ------------------
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, default="Default Product")
    category = models.ForeignKey('ProductCategory', on_delete=models.CASCADE, default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    main_image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(int(timezone.now().timestamp()))

        buffer = BytesIO()
        try:
            barcode_setting = BarcodeSettings.objects.first()
            barcode_type = barcode_setting.barcode_type if barcode_setting else 'code128'

            if barcode_type == 'qrcode':
                img = qrcode.make(self.code)
                img.save(buffer, format='PNG')
            else:
                bc_class = barcode.get_barcode_class(barcode_type)
                bc = bc_class(self.code, writer=ImageWriter())
                bc.write(buffer)

            self.barcode_image.save(f"{self.code}.png", File(buffer), save=False)

        except Exception as e:
            print(f"Barcode generation failed: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/extra_images/')

    def __str__(self):
        return f"Image for {self.product.name}"


# ------------------ CART & ORDERS ------------------
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user} - {self.product} x {self.quantity}"

    def total_price(self):
        return self.quantity * self.product.price


class Event(models.Model):
    image = models.ImageField(upload_to='events/')
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


class SubscribeSection(models.Model):
    text = models.TextField()
    placeholder = models.CharField(max_length=100, default="Enter your email")

    def __str__(self):
        return "Subscribe Section"


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class FooterLink(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class SocialLink(models.Model):
    platform = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=100)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.platform


class SecondaryHero(models.Model):
    image = models.ImageField(upload_to='secondary_hero/')
    heading = models.CharField(max_length=200)
    sub_text = models.TextField()

    def __str__(self):
        return self.heading


class Footer(models.Model):
    text = models.TextField(default="© 2025 The Floral Studio. All rights reserved.")
    background_color = models.CharField(max_length=20, default="#000000")
    text_color = models.CharField(max_length=20, default="#ffffff")
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Footer Settings"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=20, unique=True)
    billing_date = models.DateTimeField(auto_now_add=True)
    billing_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number} for Order #{self.order.id}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


# ------------------ OTHER PRODUCTS ------------------
class Carpet(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='carpets/')
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title


class GreenWall(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='greenwalls/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title


class SportsProduct(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='sports/')
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title


class ArtificialPlant(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='plants/')
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title


# ------------------ BUSINESS & TRANSACTIONS ------------------
class BusinessProfile(models.Model):
    BUSINESS_TYPES = [
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        ('others', 'Others'),
    ]

    business_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    tin = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPES, blank=True)
    business_address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    signature = models.ImageField(upload_to='business_signatures/', blank=True, null=True)

    def __str__(self):
        return self.business_name


class SellingDetail(models.Model):
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    sold_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} sold by {self.seller}"


class BuyingDetail(models.Model):
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    bought_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} bought by {self.buyer}"


class PaymentDetail(models.Model):
    order_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment {self.order_id} - {self.payment_status}"


class OrderDetail(models.Model):
    order_number = models.CharField(max_length=100)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"


class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About Us")
    content = models.TextField()

    def __str__(self):
        return "About Page Content"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


# ------------------ PAYMENTS ------------------
class Payment(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    raw_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.amount} ({self.status})"


# ------------------ DELIVERY ------------------
class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('packed', 'Packed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ]

    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='delivery')
    recipient_name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    delivery_option = models.CharField(max_length=50, default='standard')
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_delivery_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id}"
