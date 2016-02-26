from django.contrib import admin

from . import models

admin.site.register(models.DataRequestProject)
admin.site.register(models.OAuth2DataRequestProject)
admin.site.register(models.OnSiteDataRequestProject)
admin.site.register(models.DataRequestProjectMember)
