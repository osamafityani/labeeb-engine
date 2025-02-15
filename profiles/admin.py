from django.contrib import admin
from .models import Profile  # Adjust the import path according to your app structure
from django.utils.html import format_html


class ProfileAdmin(admin.ModelAdmin):
    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'User Email'  # Sets column name

    # If you want to make the email clickable (assuming email field exists in your user model)
    def user_email_link(self, obj):
        if obj.user.email:
            return format_html('<a href="mailto:{}">{}</a>', obj.user.email, obj.user.email)
        return "-"

    user_email_link.short_description = 'User Email'

    def profile_str(self, obj):
        return str(obj)

    profile_str.short_description = 'Profile'  # Sets column name

    # Uncomment the next line if you prefer the email link version
    # list_display = ()

    search_fields = ['first_name', 'last_name']
    # list_filter = ['status']
    readonly_fields = ['last_modified']  # Mark the submitted at field as read-only if it should not be editable


admin.site.register(Profile, ProfileAdmin)
