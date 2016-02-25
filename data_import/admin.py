from django.contrib import admin

from . import models

admin.site.register(models.DataFile)
admin.site.register(models.NewDataFileAccessLog)


@admin.register(models.DataRetrievalTask)
class DataRetrievalTaskAdmin(admin.ModelAdmin):
    """
    Add some additional fields and allow searching in the DataRetrievalTask
    admin view.
    """

    list_display = ('__unicode__', 'user', 'status')
    search_fields = ('user__username',)
