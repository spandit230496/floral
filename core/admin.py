from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils.html import format_html

# Import models
from .models import (
    Product, ProductImage, SellingDetail, Payment, BarcodeSettings,
    NavLink, SecondaryHero, Footer, CartItem, Carpet, GreenWall, SportsProduct,
    ArtificialPlant, BusinessProfile, BuyingDetail, PaymentDetail, OrderDetail,
    AboutPage, ContactMessage, HeroSlide, ProductCategory, Event,
    SubscribeSection, Newsletter, FooterLink, SocialLink, SiteSettings
)

# =============================
# Register simple/basic models
# =============================
admin.site.register(NavLink)


admin.site.register(Event)
admin.site.register(CartItem)
admin.site.register(SubscribeSection)
admin.site.register(Newsletter)  # Newsletter is correct model name
admin.site.register(FooterLink)
admin.site.register(SocialLink)
admin.site.register(SecondaryHero)
admin.site.register(Footer)
admin.site.register(Carpet)
admin.site.register(GreenWall)
admin.site.register(SportsProduct)
admin.site.register(ArtificialPlant)

# =============================
# Barcode-enabled Product Admin
# =============================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 10

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    inlines = [ProductImageInline]

# Only register ProductCategory once
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(BarcodeSettings)
class BarcodeSettingsAdmin(admin.ModelAdmin):
    list_display = ('barcode_type',)

# =============================
# Other Admin Configurations
# =============================
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name',)


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Business Details', {
            'fields': ('business_name', 'phone_number', 'tin', 'email', 'logo')
        }),
        ('More Details', {
            'fields': ('business_type', 'business_address', 'signature')
        }),
    )
    list_display = ('business_name', 'phone_number', 'email', 'business_type')


@admin.register(SellingDetail)
class SellingDetailAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'seller', 'quantity', 'price', 'sold_on')
    list_filter = ('sold_on', 'seller')
    search_fields = ('product_name',)


@admin.register(BuyingDetail)
class BuyingDetailAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'buyer', 'quantity', 'bought_on')
    list_filter = ('bought_on', 'buyer')
    search_fields = ('product_name',)


@admin.register(PaymentDetail)
class PaymentDetailAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'amount', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'payment_date')
    search_fields = ('order_id',)


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'buyer', 'status', 'order_date', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('order_number',)


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    ordering = ('-created_at',)


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('headline', 'subtext', 'button_text')
    search_fields = ('headline', 'subtext')


# =============================
# Custom Admin Dashboard
# =============================
class CustomAdminSite(admin.AdminSite):
    site_header = "Floral Studio Admin"
    site_title = "Floral Studio Admin Portal"
    index_title = "Dashboard Overview"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.custom_index), name='index'),
        ]
        return custom_urls + urls

    def custom_index(self, request, extra_context=None):
        total_selling = SellingDetail.objects.count()
        total_buying = BuyingDetail.objects.count()
        total_payments = PaymentDetail.objects.count()
        total_orders = OrderDetail.objects.count()

        latest_selling = SellingDetail.objects.order_by('-sold_on')[:5]
        latest_buying = BuyingDetail.objects.order_by('-bought_on')[:5]
        latest_payments = PaymentDetail.objects.order_by('-payment_date')[:5]
        latest_orders = OrderDetail.objects.order_by('-order_date')[:5]

        today = now().date()
        months = [(today.replace(day=1) - timedelta(days=i * 30)).strftime("%b %Y") for i in range(5, -1, -1)]

        selling_data_qs = (
            SellingDetail.objects
            .annotate(month=TruncMonth('sold_on'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        selling_data = {item['month'].strftime("%b %Y"): item['count'] for item in selling_data_qs}
        selling_counts = [selling_data.get(month, 0) for month in months]

        order_data_qs = (
            OrderDetail.objects
            .annotate(month=TruncMonth('order_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        order_data = {item['month'].strftime("%b %Y"): item['count'] for item in order_data_qs}
        order_counts = [order_data.get(month, 0) for month in months]

        context = {
            **(extra_context or {}),
            'total_selling': total_selling,
            'total_buying': total_buying,
            'total_payments': total_payments,
            'total_orders': total_orders,
            'months': months,
            'selling_counts': selling_counts,
            'order_counts': order_counts,
            'latest_selling': latest_selling,
            'latest_buying': latest_buying,
            'latest_payments': latest_payments,
            'latest_orders': latest_orders,
        }
        return TemplateResponse(request, "admin/custom_index.html", context)


custom_admin_site = CustomAdminSite(name='custom_admin')
custom_admin_site.register(BusinessProfile)
custom_admin_site.register(SellingDetail)
custom_admin_site.register(BuyingDetail)
custom_admin_site.register(PaymentDetail)
custom_admin_site.register(OrderDetail)

# =============================
# Graph Data
# =============================
@staff_member_required
def admin_dashboard(request):
    product_count = Product.objects.count()
    selling_count = SellingDetail.objects.count()
    payment_count = Payment.objects.count()

    context = {
        'product_count': product_count,
        'selling_count': selling_count,
        'payment_count': payment_count,
    }
    return render(request, "admin_dashboard.html", context)


@staff_member_required
def dashboard_data(request):
    data = {
        "total_products": Product.objects.count(),
        "total_sells": SellingDetail.objects.count(),
        "total_users": User.objects.count(),
        "total_payments": Payment.objects.count(),
    }
    return JsonResponse(data)

# =============================



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'amount', 'status', 'created_at')
    search_fields = ('user__username', 'razorpay_payment_id', 'razorpay_order_id')
    readonly_fields = ('raw_response',)
