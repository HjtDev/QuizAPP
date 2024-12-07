from django.contrib import admin
from .models import Player
from django.contrib.auth.models import Group

admin.site.unregister(Group)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'score', 'league', 'phone', 'name', 'is_active')
    list_filter = ('league', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('phone', 'name', 'id', 'display_name', 'score')
    date_hierarchy = 'created_at'
    list_per_page = 30

    fieldsets = (
        (None, {
            'fields': ('phone', 'name', 'display_name', 'is_active')
        }),
        ('Game', {
            'fields': ('score', 'league'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
