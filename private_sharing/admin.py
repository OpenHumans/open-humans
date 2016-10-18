from django.contrib import admin

from . import models


class DataRequestProjectMemberAdmin(admin.ModelAdmin):
    """
    Display and make the 'created' field read-only in the admin interface.
    """

    readonly_fields = ('created',)
    search_fields = ('member__user__username',
                     'project_member_id',
                     'project__name')


admin.site.register(models.ProjectDataFile)
admin.site.register(models.DataRequestProject)
admin.site.register(models.OAuth2DataRequestProject)
admin.site.register(models.OnSiteDataRequestProject)
admin.site.register(models.DataRequestProjectMember,
                    DataRequestProjectMemberAdmin)
