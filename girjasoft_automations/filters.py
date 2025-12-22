"""
girjasoft_automations/filters.py
"""

from girjasoft.filters import GirjasoftFilterSet, django_filters
from girjasoft_automations.models import MailAutomation


class AutomationFilter(GirjasoftFilterSet):
    """
    AutomationFilter
    """

    search = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = MailAutomation
        fields = "__all__"
