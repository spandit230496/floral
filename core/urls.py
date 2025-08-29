# core/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import signup_view, invoice_view
from django.contrib.auth.views import LogoutView
from .views import signup_view, invoice_view, subscribe_newsletter

from core import admin_views

urlpatterns = [
    # 🏠 Home page
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),

    # Authentication
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Password Reset Flow
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # 🛒 Cart functionality
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),

    # 💳 Checkout
    path('order-success/', views.order_success, name='order_success'),
    path('checkout/', views.checkout, name='checkout_no_order'),  # Optional checkout without order_id
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),

    path('payment/verify/', views.payment_verify, name='payment_verify'),
    path('razorpay/webhook/', views.razorpay_webhook, name='razorpay_webhook'),

    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    
    # Products
    path('carpet/', views.carpet_view, name='carpet'),
    path('carpets/', views.carpet_view, name='carpet_view'),

    path('greenwalls/', views.greenwalls_view, name='greenwalls_view'),
    path('sports/', views.sports_view, name='sports_view'),

    path('artificialplants/', views.artificial_plants_view, name='artificialplants_view'),
    path('artificial-plants/', views.artificial_plants_view, name='artificial_plants'),

    # Newsletter subscription
    path('subscribe/', subscribe_newsletter, name='subscribe_newsletter'),


    # Contact page
    path('contact/', views.contact_view, name='contact'),

    # Invoice view (make sure user is logged in to view)
    path('invoice/<int:order_id>/', invoice_view, name='invoice'),
    path('invoice/', invoice_view, name='invoice'),
    # Admin dashboard
    path('admin-dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),

    #microtechnique
    path("access-admin/", views.access_floral_admin, name="access_floral_admin"),
]
