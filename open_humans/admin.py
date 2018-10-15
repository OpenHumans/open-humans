from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Member, User, GrantProject

admin.site.register(Member)
admin.site.register(User, UserAdmin)
