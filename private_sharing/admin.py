from django.contrib import admin

from . import models


class DataRequestProjectMemberAdmin(admin.ModelAdmin):
    """
    Display and make the 'created' field read-only in the admin interface.
    """

    readonly_fields = ("created",)
    search_fields = ("member__user__username", "project_member_id", "project__name")
    raw_id_fields = ("member",)

    def get_queryset(self, request):
        """
        Go ahead and fetch the member model to speed up the admin page load a bit
        """
        return super().get_queryset(request).select_related("member")


class DataRequestProjectAdmin(admin.ModelAdmin):
    """
    select_related the coordinator field and set to be raw_id
    """

    raw_id_fields = ("coordinator",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("coordinator")


admin.site.register(models.ProjectDataFile)
admin.site.register(models.DataRequestProject, DataRequestProjectAdmin)
admin.site.register(models.OAuth2DataRequestProject, DataRequestProjectAdmin)
admin.site.register(models.OnSiteDataRequestProject, DataRequestProjectAdmin)
admin.site.register(models.DataRequestProjectMember, DataRequestProjectMemberAdmin)
admin.site.register(models.FeaturedProject)
