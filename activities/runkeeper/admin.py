from django.contrib import admin

from .models import DataFile, UserData

admin.site.register(DataFile)
admin.site.register(UserData)
