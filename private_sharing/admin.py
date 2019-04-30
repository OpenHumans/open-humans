from django.contrib import admin

from . import models


class DataRequestProjectMemberAdmin(admin.ModelAdmin):
    """
    Display and make the 'created' field read-only in the admin interface.
    """

    readonly_fields = ("created",)
    search_fields = ("member__user__username", "project_member_id", "project__name")
    raw_id_fields = ("member",)


class DataRequestProjectAdmin(admin.ModelAdmin):
    """
    set the coordinator field to be raw_id
    """

    raw_id_fields = ("coordinator",)


admin.site.register(models.ProjectDataFile)
admin.site.register(models.DataRequestProject, DataRequestProjectAdmin)
admin.site.register(models.OAuth2DataRequestProject, DataRequestProjectAdmin)
admin.site.register(models.OnSiteDataRequestProject, DataRequestProjectAdmin)
admin.site.register(models.DataRequestProjectMember, DataRequestProjectMemberAdmin)
admin.site.register(models.FeaturedProject)
