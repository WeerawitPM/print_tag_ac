from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Tag, RefTag

# Register your models here.
class TagAdmin(admin.ModelAdmin):
    list_display = ('qr_code', 'part_no', 'part_code', 'part_name', 'model_name', 'stock_inout', 'date', 'whouse_code', 'ref_tag_link')  # Updated field names
    search_fields = ('qr_code', 'part_no', 'part_code', 'part_name', 'model_name', 'stock_inout', 'date', 'whouse_code')  # Updated field names
    list_filter = ('date', 'part_no', 'whouse_code')
    ordering = ('date',)
    
    def ref_tag_link(self, obj):
        if obj.ref_tag:
            url = reverse('admin:%s_%s_change' % (obj.ref_tag._meta.app_label, obj.ref_tag._meta.model_name), args=[obj.ref_tag.pk])
            return format_html('<a href="{}">{}</a>', url, obj.ref_tag)
        return "-"
    ref_tag_link.short_description = 'Ref Tag'

class RefTagAdmin(admin.ModelAdmin):
    list_display = ('ref_id',)
    search_fields = ('ref_id',)
    
admin.site.register(Tag, TagAdmin)
admin.site.register(RefTag, RefTagAdmin)