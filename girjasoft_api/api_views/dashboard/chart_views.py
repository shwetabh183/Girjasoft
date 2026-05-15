"""
JSON chart payloads for the Next.js dashboard (legacy Chart.js parity).
"""

from __future__ import annotations

from datetime import date

from django.apps import apps
from django.utils.translation import gettext as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.filters import AttendanceOverTimeFilter
from attendance.methods.utils import pending_hour_data, worked_hour_data
from attendance.models import AttendanceOverTime
from attendance.views.dashboard import generate_data_set
from base.models import Department
from employee.models import Employee, EmployeeWorkInformation
from leave.filters import LeaveRequestFilter
from leave.models import LeaveRequest


def _is_reporting_manager(user) -> bool:
    employee = getattr(user, "employee_get", None)
    if not employee:
        return False
    return EmployeeWorkInformation.objects.filter(reporting_manager_id=employee).exists()


def _employee_chart_queryset(request):
    user = request.user
    if user.has_perm("employee.view_employee"):
        return Employee.objects.all()
    managed = EmployeeWorkInformation.objects.filter(
        reporting_manager_id=getattr(user, "employee_get", None)
    ).values_list("employee_id", flat=True)
    if managed.exists():
        return Employee.objects.filter(id__in=managed)
    return Employee.objects.none()


class DashboardChartEmployeeActiveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (
            request.user.has_perm("employee.view_employee") or _is_reporting_manager(request.user)
        ):
            return Response({"error": "Permission denied"}, status=403)

        employees = _employee_chart_queryset(request)
        labels = [_("Active"), _("In-Active")]
        return Response(
            {
                "labels": labels,
                "dataSet": [
                    {
                        "label": _("Employees"),
                        "data": [
                            employees.filter(is_active=True).count(),
                            employees.filter(is_active=False).count(),
                        ],
                    }
                ],
            }
        )


class DashboardChartEmployeeGenderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (
            request.user.has_perm("employee.view_employee") or _is_reporting_manager(request.user)
        ):
            return Response({"error": "Permission denied"}, status=403)

        employees = _employee_chart_queryset(request).filter(is_active=True)
        labels = [_("Male"), _("Female"), _("Other")]
        return Response(
            {
                "labels": labels,
                "dataSet": [
                    {
                        "label": _("Employees"),
                        "data": [
                            employees.filter(gender="male").count(),
                            employees.filter(gender="female").count(),
                            employees.filter(gender="other").count(),
                        ],
                    }
                ],
            }
        )


class DashboardChartEmployeeDepartmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (
            request.user.has_perm("employee.view_employee") or _is_reporting_manager(request.user)
        ):
            return Response({"error": "Permission denied"}, status=403)

        employees = _employee_chart_queryset(request).filter(is_active=True)
        labels = []
        count = []
        for dept in Department.objects.all():
            n = employees.filter(employee_work_info__department_id=dept).count()
            if n:
                labels.append(dept.department)
                count.append(n)
        return Response(
            {
                "labels": labels,
                "dataSet": [{"label": "Department", "data": count}],
                "message": _("No Data Found..."),
            }
        )


class DashboardChartOverallLeaveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not apps.is_installed("leave"):
            return Response({"labels": [], "data": []})
        if not (
            request.user.has_perm("leave.view_leaverequest") or _is_reporting_manager(request.user)
        ):
            return Response({"error": "Permission denied"}, status=403)

        labels = []
        data = []
        leave_requests = LeaveRequestFilter(request.GET, queryset=LeaveRequest.objects.all()).qs
        for department in Department.objects.all():
            count = leave_requests.filter(
                employee_id__employee_work_info__department_id=department
            ).count()
            if count:
                labels.append(department.department)
                data.append(count)
        return Response({"labels": labels, "data": data})


class DashboardChartAttendanceAnalyticAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not apps.is_installed("attendance"):
            return Response({"dataSet": [], "labels": [], "message": _("No records available at the moment.")})
        if not (
            request.user.has_perm("attendance.view_attendance") or _is_reporting_manager(request.user)
        ):
            return Response({"error": "Permission denied"}, status=403)

        django_request = getattr(request, "_request", request)
        labels = [_("On Time"), _("Late Come"), _("Early Out")]
        start_date = django_request.GET.get("date") or date.today().isoformat()
        end_date = django_request.GET.get("end_date") or start_date
        period_type = django_request.GET.get("type") or "day"

        data_set = []
        for dept in Department.objects.all():
            row = generate_data_set(django_request, start_date, period_type, end_date, dept)
            data_set.append(row)
        data_set = [row for row in data_set if row]
        return Response(
            {
                "dataSet": data_set,
                "labels": labels,
                "message": _("No records available at the moment."),
            }
        )


class DashboardChartPendingHoursAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not apps.is_installed("attendance"):
            return Response({"data": {"labels": [], "datasets": []}})
        if not (
            request.user.has_perm("attendance.view_attendance") or _is_reporting_manager(request.user)
        ):
            return Response({"error": "Permission denied"}, status=403)

        django_request = getattr(request, "_request", request)
        records = AttendanceOverTimeFilter(
            django_request.GET,
            queryset=AttendanceOverTime.objects.all(),
        ).qs
        labels = list(Department.objects.values_list("department", flat=True))
        payload = {
            "labels": labels,
            "datasets": [
                pending_hour_data(labels, records),
                worked_hour_data(labels, records),
            ],
        }
        return Response({"data": payload})


def _bar_chart_colors(count: int):
    import random

    backgrounds = []
    borders = []
    for _ in range(count):
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        backgrounds.append(f"rgba({red}, {green}, {blue}, 0.35)")
        borders.append(f"rgb({red}, {green}, {blue})")
    return backgrounds, borders


class DashboardChartHiredCandidatesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not apps.is_installed("recruitment"):
            return Response({"labels": [], "data": [], "background_color": [], "border_color": []})
        from recruitment.models import Recruitment

        labels = []
        data = []
        backgrounds, borders = [], []
        for recruitment in Recruitment.objects.filter(closed=False, is_active=True):
            labels.append(str(recruitment))
            data.append(recruitment.candidate.filter(hired=True).count())
        backgrounds, borders = _bar_chart_colors(len(labels))
        return Response(
            {
                "labels": labels,
                "data": data,
                "background_color": backgrounds,
                "border_color": borders,
                "message": _("No records available at the moment."),
            }
        )


class DashboardChartOnboardingCandidatesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not apps.is_installed("recruitment"):
            return Response({"labels": [], "data": [], "background_color": [], "border_color": []})
        from recruitment.models import Recruitment

        labels = []
        data = []
        for recruitment in Recruitment.objects.filter(closed=False, is_active=True):
            labels.append(recruitment.title or str(recruitment))
            data.append(recruitment.candidate.filter(start_onboard=True).count())
        backgrounds, borders = _bar_chart_colors(len(labels))
        return Response(
            {
                "labels": labels,
                "data": data,
                "background_color": backgrounds,
                "border_color": borders,
                "message": _("No records available at the moment."),
            }
        )


class DashboardChartRecruitmentPipelineAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not apps.is_installed("recruitment"):
            return Response({"dataSet": [], "labels": [], "message": _("No records available at the moment.")})
        from recruitment.models import Recruitment, Stage

        def stage_count(recruitment, stage_type):
            total = 0
            for stage in recruitment.stage_set.filter(stage_type=stage_type):
                total += stage.candidate_set.filter(is_active=True).count()
            return total

        labels = [label for _, label in Stage.stage_types]
        data_set = []
        for recruitment in Recruitment.objects.filter(closed=False):
            counts = [stage_count(recruitment, st[0]) for st in Stage.stage_types]
            if any(counts):
                data_set.append(
                    {
                        "label": recruitment.title or str(recruitment),
                        "data": counts,
                    }
                )
        return Response(
            {
                "dataSet": data_set,
                "labels": labels,
                "message": _("No records available at the moment."),
            }
        )


class DashboardChartObjectiveStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not apps.is_installed("pms"):
            return Response({"labels": [], "data": []})
        from base.methods import filtersubordinates
        from pms.models import EmployeeObjective

        labels = []
        data = []
        for status_code, status_label in EmployeeObjective.STATUS_CHOICES:
            qs = EmployeeObjective.objects.filter(status=status_code, archive=False)
            count = filtersubordinates(
                request, queryset=qs, perm="pms.view_employeeobjective"
            ).count()
            if count:
                labels.append(str(status_label))
                data.append(count)
        return Response({"labels": labels, "data": data})


class DashboardChartKeyResultStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not apps.is_installed("pms"):
            return Response({"labels": [], "data": []})
        from base.methods import filtersubordinates
        from pms.models import EmployeeKeyResult

        labels = []
        data = []
        for status_code, status_label in EmployeeKeyResult.STATUS_CHOICES:
            qs = EmployeeKeyResult.objects.filter(status=status_code)
            count = filtersubordinates(
                request,
                queryset=qs,
                perm="pms.view_employeekeyresult",
                field="employee_objective_id__employee_id",
            ).count()
            if count:
                labels.append(str(status_label))
                data.append(count)
        return Response({"labels": labels, "data": data})


class DashboardChartFeedbackStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not apps.is_installed("pms"):
            return Response({"labels": [], "data": []})
        from base.methods import filtersubordinates
        from pms.models import Feedback

        labels = []
        data = []
        for status_code, status_label in Feedback.STATUS_CHOICES:
            qs = Feedback.objects.filter(status=status_code)
            count = filtersubordinates(request, queryset=qs, perm="pms.view_feedback").count()
            if count:
                labels.append(str(status_label))
                data.append(count)
        return Response({"labels": labels, "data": data})
