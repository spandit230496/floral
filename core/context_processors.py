from .models import NavbarLogo, NavbarMenuItem
from .models import SiteSettings

def navbar_context(request):
    return {
        'navbar_logo': NavbarLogo.objects.all(),
        'navbar_menu_items': NavbarMenuItem.objects.all()
    }
from .models import SiteSettings

def site_settings(request):
    settings = SiteSettings.objects.first()
    return {'site_settings': settings}