from django.contrib import admin

from .models import DataRetrievalTask


@admin.register(DataRetrievalTask)
class DataRetrievalTaskAdmin(admin.ModelAdmin):
    """
    Add some additional fields and allow searching in the DataRetrievalTask
    admin view.
    """

    list_display = ('__unicode__', 'user', 'status')
    search_fields = ('user__username',)
