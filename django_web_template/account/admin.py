from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from account.models import PlatformUser

class PlatformUserAdmin(BaseUserAdmin):
    list_display = ('phone', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('phone',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    search_fields = ('phone',)
    ordering = ('created',)
    filter_horizontal = ()


admin.site.register(PlatformUser, PlatformUserAdmin)
