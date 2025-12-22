"""
admin.py
"""

from django.contrib import admin

from girjasoft_audit.models import AuditTag, GirjasoftAuditInfo, GirjasoftAuditLog

# Register your models here.

admin.site.register(AuditTag)
