from django.db import migrations

def set_default_category(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    ProductCategory = apps.get_model('core', 'ProductCategory')

    default_cat = ProductCategory.objects.get(name="Default Category")
    Product.objects.filter(category__isnull=True).update(category=default_cat)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_alter_product_category'),  # change this if your last migration number is different
    ]

    operations = [
        migrations.RunPython(set_default_category),
    ]
