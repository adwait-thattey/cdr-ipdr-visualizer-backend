from django.contrib import admin

from .models import Person
from .models import Mobile

admin.site.register(Person)

admin.site.register(Mobile)
