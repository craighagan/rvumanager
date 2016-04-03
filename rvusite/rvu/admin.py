from django.contrib import admin

# Register your models here.
from .models import Provider, BillingCode, PatientVisit

admin.site.register(Provider)
admin.site.register(BillingCode)
admin.site.register(PatientVisit)

