from django.contrib import admin

from .models import DataRequest, Researcher, Study, StudyGrant

admin.site.register(DataRequest)
admin.site.register(Researcher)
admin.site.register(Study)
admin.site.register(StudyGrant)
