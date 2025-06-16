from django.contrib import admin
from .models import CalendarConnection, O365Token

@admin.register(CalendarConnection)
class CalendarConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_expiry', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('OAuth Information', {
            'fields': ('microsoft_token', 'refresh_token', 'token_expiry', 'flow')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(O365Token)
class O365TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('last_updated',)
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Token Information', {
            'fields': ('token',)
        }),
        ('Timestamps', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
