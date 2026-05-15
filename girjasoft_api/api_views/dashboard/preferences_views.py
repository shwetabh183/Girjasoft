"""Dashboard preferences: hidden tiles, overtime queue, feedback to answer."""

from __future__ import annotations

import json

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.models import Attendance, AttendanceValidationCondition
from attendance.views.views import strtime_seconds
from base.methods import filtersubordinates
from base.models import DashboardEmployeeCharts
from girjasoft_api.api_views.dashboard.tile_map import (
    chart_id_for_tile,
    hidden_tile_ids,
)
from girjasoft_api.api_serializers.attendance.serializers import AttendanceSerializer


class DashboardHiddenChartsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = getattr(request.user, "employee_get", None)
        if not employee:
            return Response({"hidden_chart_ids": [], "hidden_tile_ids": []})
        record = DashboardEmployeeCharts.objects.filter(employee=employee).first()
        chart_ids = list(record.charts) if record and record.charts else []
        return Response(
            {
                "hidden_chart_ids": chart_ids,
                "hidden_tile_ids": hidden_tile_ids(chart_ids),
            }
        )

    def post(self, request):
        """Hide a tile (legacy dashboard-components-toggle parity)."""
        employee = getattr(request.user, "employee_get", None)
        if not employee:
            return Response({"error": "No employee profile"}, status=400)

        chart_id = request.data.get("chart_id") or request.query_params.get("chart_id")
        tile_id = request.data.get("tile_id")
        if tile_id and not chart_id:
            chart_id = chart_id_for_tile(tile_id)
        if not chart_id:
            return Response({"error": "chart_id or tile_id required"}, status=400)

        record, _ = DashboardEmployeeCharts.objects.get_or_create(employee=employee)
        charts = list(record.charts or [])
        if chart_id not in charts:
            charts.append(chart_id)
            record.charts = charts
            record.save(update_fields=["charts"])
        return Response(
            {
                "hidden_chart_ids": charts,
                "hidden_tile_ids": hidden_tile_ids(charts),
            }
        )

    def delete(self, request):
        """Restore a hidden tile."""
        employee = getattr(request.user, "employee_get", None)
        if not employee:
            return Response({"error": "No employee profile"}, status=400)

        chart_id = request.data.get("chart_id") or request.query_params.get("chart_id")
        tile_id = request.data.get("tile_id")
        if tile_id and not chart_id:
            chart_id = chart_id_for_tile(tile_id)
        if not chart_id:
            return Response({"error": "chart_id or tile_id required"}, status=400)

        record = DashboardEmployeeCharts.objects.filter(employee=employee).first()
        if not record or not record.charts:
            return Response({"hidden_chart_ids": [], "hidden_tile_ids": []})

        charts = [cid for cid in record.charts if cid != chart_id]
        record.charts = charts
        record.save(update_fields=["charts"])
        return Response(
            {
                "hidden_chart_ids": charts,
                "hidden_tile_ids": hidden_tile_ids(charts),
            }
        )


class DashboardOvertimePendingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        condition = AttendanceValidationCondition.objects.first()
        min_ot = strtime_seconds("00:00")
        if condition is not None and condition.minimum_overtime_to_approve is not None:
            min_ot = strtime_seconds(condition.minimum_overtime_to_approve)

        queryset = Attendance.objects.filter(
            overtime_second__gte=min_ot,
            attendance_validated=True,
            employee_id__is_active=True,
            attendance_overtime_approve=False,
        )
        queryset = filtersubordinates(
            request=request,
            perm="attendance.change_attendance",
            queryset=queryset,
        ).select_related("employee_id", "shift_id")

        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(queryset.order_by("-attendance_date"), request)
        serializer = AttendanceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DashboardFeedbackPendingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.apps import apps

        if not apps.is_installed("pms"):
            return Response({"count": 0, "results": []})

        from pms.models import Feedback

        employee = getattr(request.user, "employee_get", None)
        if not employee:
            return Response({"count": 0, "results": []})

        feedback_requested = Feedback.objects.filter(
            Q(manager_id=employee, manager_id__is_active=True)
            | Q(colleague_id=employee, colleague_id__is_active=True)
            | Q(subordinate_id=employee, subordinate_id__is_active=True)
        ).distinct()
        pending = feedback_requested.exclude(feedback_answer__employee_id=employee)

        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(pending.order_by("-id"), request)
        results = [
            {
                "id": fb.id,
                "title": fb.feedback_title or "",
                "status": fb.status,
                "employee_name": (
                    fb.employee_id.get_full_name() if fb.employee_id else ""
                ),
                "period": fb.review_cycle if hasattr(fb, "review_cycle") else "",
            }
            for fb in page
        ]
        return paginator.get_paginated_response(results)
