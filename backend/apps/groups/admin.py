from django.contrib import admin
from .models import FarmerGroup, GroupLoanHistory


class GroupLoanHistoryInline(admin.TabularInline):
    model = GroupLoanHistory
    extra = 0


@admin.register(FarmerGroup)
class FarmerGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'group_type', 'district', 'sub_county', 'is_approved', 'member_count', 'created_at']
    list_filter = ['group_type', 'district', 'is_approved', 'is_registered']
    search_fields = ['name', 'district', 'chairperson_name', 'registration_number']
    readonly_fields = ['id', 'created_at', 'updated_at', 'approved_at', 'member_count', 'total_land_acres']
    inlines = [GroupLoanHistoryInline]

    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Members'
