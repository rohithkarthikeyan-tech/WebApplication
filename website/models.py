import uuid
from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('General', 'General Platform'),
        ('Authentication', 'Authentication & Access'),
        ('Security', 'Security & CSRF'),
        ('Error Codes', 'Error Codes & Troubleshooting'),
        ('Architecture', 'Architecture & Databases'),
        ('AI Assistant', 'AI Assistant & Support'),
    ]

    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='General')
    keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords for AI search matching")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Frequently Asked Question'
        verbose_name_plural = 'Frequently Asked Questions'

    def __str__(self):
        return f"[{self.category}] {self.question}"


class ErrorCode(models.Model):
    CATEGORY_CHOICES = [
        ('Client Error', 'Client Error (4xx)'),
        ('Server Error', 'Server Error (5xx)'),
        ('Site-Specific', 'Site-Specific Custom Error'),
    ]

    code = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    summary = models.CharField(max_length=255)
    description = models.TextField()
    resolution = models.TextField()
    ai_guidance = models.TextField(help_text="Context given to the AI assistant for troubleshooting")

    class Meta:
        ordering = ['code']
        verbose_name = 'Error Code Reference'
        verbose_name_plural = 'Error Code References'

    def __str__(self):
        return f"{self.code} - {self.title}"


class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low Priority'),
        ('Medium', 'Medium Priority'),
        ('High', 'High Priority'),
        ('Critical', 'Critical Emergency'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    SOURCE_CHOICES = [
        ('AI Assistant', 'AI Assistant Escalation'),
        ('Web Form', 'Web Support Portal'),
        ('Error Page', 'Error Page Escalation'),
    ]

    ticket_number = models.CharField(max_length=32, unique=True, editable=False)
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='AI Assistant')
    associated_error_code = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            uid = uuid.uuid4().hex[:6].upper()
            self.ticket_number = f"TICK-{uid}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} - {self.subject} ({self.status})"
