from django.contrib import admin

from .models import Person, MobileNumber, SimCard, Device, CDR, IPDR, WatchList, TrackedObject, Alert

admin.site.register((Person, MobileNumber, SimCard, Device, CDR, IPDR, WatchList, TrackedObject, Alert))
