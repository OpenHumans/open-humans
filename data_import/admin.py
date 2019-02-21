from django.contrib import admin

from . import models

admin.site.register(models.DataFile)
admin.site.register(models.NewDataFileAccessLog)
admin.site.register(models.DataTypes)
