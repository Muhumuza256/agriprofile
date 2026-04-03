from django.contrib import admin
from .models import ImpactSnapshot


@admin.register(ImpactSnapshot)
class ImpactSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'group', 'snapshot_type', 'snapshot_date', 'member_count',
        'gacs_at_snapshot', 'financial_inclusion_rate',
    ]
    list_filter = ['snapshot_type']
    search_fields = ['group__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'financial_inclusion_rate']
