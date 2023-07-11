from django.contrib import admin

# Register your models here.

from tienda_app.models import Productor

@admin.register(Productor)
class ProductorAdmin(admin.ModelAdmin):
    list_display = ['nombrecontacto', 'RUT', 'razonsocial', 'direccion', 'comuna']
    search_fields = ['nombrecontacto', 'razonsocial']