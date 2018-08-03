from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import GrantProject, Member, User


admin.site.register(Member)
admin.site.register(User, UserAdmin)


class GrantProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GrantProject._meta.get_fields()]


admin.site.register(GrantProject, GrantProjectAdmin)
