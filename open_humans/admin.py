from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Member, User, GrantProject


class MemberAdmin(admin.ModelAdmin):
    """
    Speed up loading users
    """

    raw_id_fields = ("user",)
    search_fields = ("user__username", "user__email")


admin.site.register(Member, MemberAdmin)
admin.site.register(User, UserAdmin)


class GrantProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GrantProject._meta.get_fields()]


admin.site.register(GrantProject, GrantProjectAdmin)
