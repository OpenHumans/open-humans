from django.contrib import admin

from .models import DataRetrievalTask

@admin.register(DataRetrievalTask)
class DataRetrievalTaskAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user', 'status')
    search_fields = ('user__username',)
