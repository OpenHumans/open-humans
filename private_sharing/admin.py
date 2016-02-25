from django.contrib import admin

from . import models

admin.site.register(models.DataRequestActivity)
admin.site.register(models.OAuth2DataRequestActivity)
admin.site.register(models.OnSiteDataRequestActivity)
admin.site.register(models.DataRequestActivityMember)
