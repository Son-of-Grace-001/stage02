from django.contrib import admin
from .models import CustomUser, Organisation

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Organisation)
