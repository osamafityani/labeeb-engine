from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['created_at']  # Mark the created field as read-only if it should not be editable


admin.site.register(CustomUser, CustomUserAdmin)
