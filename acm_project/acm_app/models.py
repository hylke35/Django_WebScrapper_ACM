from .enums import CompanyStatus
from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=11, choices=CompanyStatus.choices(), null=False, blank=False)
    scanned_supplier = models.ForeignKey('ScannedSupplier', blank=True, null=True, on_delete=models.CASCADE)

    @classmethod
    def create(cls, name, status, scanned_supplier):
        return cls(name=name, status=status, scanned_supplier=scanned_supplier)

class ScannedSupplier(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to='images/', null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)

    @classmethod
    def create(cls, name, status, website):
        return cls(name=name, logo=status, website=website)