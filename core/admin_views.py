from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncDate
from core.models import Product, SellingDetail, Payment
from django.contrib.auth.models import User

def admin_dashboard(request):
    product_count = Product.objects.count()
    user_count = User.objects.count()
    sell_counts = SellingDetail.objects.annotate(
        day=TruncDate('sold_on')
    ).values('day').annotate(
        total=Count('id')
    ).order_by('day')

    print("Sell counts:", list(sell_counts))  # Add this debug line

    payment_count = Payment.objects.count()

    context = {
        "product_count": product_count,
        "user_count": user_count,
        "sell_counts": sell_counts,
        "payment_count": payment_count,
    }
    return render(request, "admin_dashboard.html", context)
