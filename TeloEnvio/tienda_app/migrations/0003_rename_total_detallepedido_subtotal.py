# Generated by Django 4.2.3 on 2023-07-11 17:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tienda_app', '0002_producto_productor'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detallepedido',
            old_name='total',
            new_name='subtotal',
        ),
    ]
