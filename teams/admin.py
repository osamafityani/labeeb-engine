from django.contrib import admin
from .models import Team, TeamMember


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'created_at', 'last_modified')
    search_fields = ['name', 'company']
    readonly_fields = ['created_at', 'last_modified']


class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'created_at', 'last_modified')
    search_fields = ['name', 'team__name']
    list_filter = ['team']
    readonly_fields = ['created_at', 'last_modified']


admin.site.register(Team, TeamAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
