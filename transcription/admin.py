from django.contrib import admin
from .models import Meeting, Project
import numpy as np


def format_embeddings(obj):
    """Format embeddings for display in admin"""
    if obj.embeddings is not None:
        # Convert to list and truncate for display
        embeddings_list = obj.embeddings.tolist()[:5]  # Show first 5 values
        return f"[{', '.join(f'{x:.4f}' for x in embeddings_list)}...]"
    return "No embeddings"
format_embeddings.short_description = 'Embeddings (truncated)'


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'team_account', 'type', 'code', 'start_date', 'end_date')
    search_fields = ['title', 'description', 'team', 'code']
    list_filter = ['type', 'team_account']


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'created_at')
    search_fields = ['title', 'project__title']
    list_filter = ['status', 'project']
    readonly_fields = ['created_at', 'timestamp', format_embeddings]
    
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # Replace 'embeddings' with our formatted version
        if 'embeddings' in fields:
            fields = [f if f != 'embeddings' else format_embeddings for f in fields]
        return fields


admin.site.register(Project, ProjectAdmin)
admin.site.register(Meeting, MeetingAdmin)
