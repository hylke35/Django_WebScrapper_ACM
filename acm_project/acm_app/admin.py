from django.contrib import admin
from .models import Supplier, ScannedSupplier
# Register your models here.

admin.site.register(Supplier)
admin.site.register(ScannedSupplier)