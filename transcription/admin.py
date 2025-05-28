from django.contrib import admin
from .models import Meeting, Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'team_account', 'type', 'code', 'start_date', 'end_date')
    search_fields = ['title', 'description', 'team', 'code']
    list_filter = ['type', 'team_account']


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'created_at')
    search_fields = ['title', 'project__title']
    list_filter = ['status', 'project']
    readonly_fields = ['created_at', 'timestamp', 'embeddings']


admin.site.register(Project, ProjectAdmin)
admin.site.register(Meeting, MeetingAdmin)
