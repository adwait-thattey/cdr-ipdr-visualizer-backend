from django.contrib import admin

from .models import Person, MobileNumber, SimCard, Device, WatchList, TrackedObject, Alert, CDR, IPDR

admin.site.register((Person, MobileNumber, SimCard, Device, WatchList, TrackedObject, Alert))


class CDRAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CDR._meta.get_fields()]


admin.site.register(CDR, CDRAdmin)


class IPDRAdmin(admin.ModelAdmin):
    list_display = [field.name for field in IPDR._meta.get_fields()]


admin.site.register(IPDR, IPDRAdmin)
