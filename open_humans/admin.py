from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FeatureFlag, GrantProject, Member, User


class MemberAdmin(admin.ModelAdmin):
    """
    Speed up loading users
    """

    raw_id_fields = ("user",)
    search_fields = ("user__username", "user__email")


class FlagAdmin(admin.ModelAdmin):
    """
    With improved User management.
    """

    raw_id_fields = ("users",)


class GrantProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GrantProject._meta.get_fields()]


admin.site.register(Member, MemberAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(FeatureFlag, FlagAdmin)
admin.site.register(GrantProject, GrantProjectAdmin)
