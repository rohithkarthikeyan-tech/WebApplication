from django.contrib import admin
from .models import ContactMessage, FAQ, ErrorCode, SupportTicket


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer', 'keywords')
    list_editable = ('order', 'is_active')


@admin.register(ErrorCode)
class ErrorCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'category', 'summary')
    list_filter = ('category',)
    search_fields = ('code', 'title', 'description', 'resolution')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'subject', 'name', 'email', 'priority', 'status', 'source', 'created_at')
    list_filter = ('status', 'priority', 'source', 'created_at')
    search_fields = ('ticket_number', 'subject', 'name', 'email', 'description')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at')
