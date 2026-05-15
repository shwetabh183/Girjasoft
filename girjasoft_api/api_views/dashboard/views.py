from __future__ import annotations

from datetime import date, timedelta

from django.apps import apps
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from base.methods import filtersubordinates, filtersubordinatesemployeemodel
from employee.filters import EmployeeFilter
from employee.models import Employee, EmployeeWorkInformation
from employee.views import birthday
from girjasoft.methods import get_girjasoft_model_class
from leave.methods import filter_conditional_leave_request
from leave.models import LeaveRequest


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        employee = getattr(user, "employee_get", None)
        is_manager = (
            EmployeeWorkInformation.objects.filter(reporting_manager_id=employee)
            .only("id")
            .exists()
            if employee
            else False
        )

        if user.has_perm("employee.view_employee"):
            total_employees = Employee.objects.filter(is_active=True).count()
        elif employee:
            subordinates = employee.get_subordinate_employees()
            total_employees = (
                subordinates.filter(is_active=True).count()
                if subordinates.exists()
                else 1
            )
        else:
            total_employees = 0

        on_leave_today = LeaveRequest.employees_on_leave_today(status="approved").count()

        joining_today = 0
        joining_week = 0
        if apps.is_installed("recruitment"):
            Candidate = get_girjasoft_model_class(
                app_label="recruitment",
                model="candidate",
            )
            joining_today = Candidate.objects.filter(
                joining_date__range=[date.today(), date.today() + timedelta(days=1)],
                is_active=True,
            ).count()
            joining_week = Candidate.objects.filter(
                joining_date__range=[
                    date.today() - timedelta(days=date.today().weekday()),
                    date.today() + timedelta(days=6 - date.today().weekday()),
                ],
                is_active=True,
                hired=True,
            ).count()

        offline_count = None
        online_count = None
        if user.has_perm("employee.view_employee") or is_manager:
            offline_count = (
                EmployeeFilter({"not_in_yet": date.today()})
                .qs.exclude(employee_work_info__isnull=True)
                .filter(is_active=True)
                .count()
            )
            online_count = (
                EmployeeFilter({"not_out_yet": date.today()})
                .qs.exclude(employee_work_info__isnull=True)
                .filter(is_active=True)
                .count()
            )

        pending_leave = None
        if user.has_perm("leave.view_leaverequest") or is_manager:
            leave_requests = LeaveRequest.objects.all()
            queryset = filtersubordinates(
                request,
                leave_requests,
                "leave.view_leaverequest",
            ) | filter_conditional_leave_request(request)
            pending_leave = queryset.filter(status="requested").count()

        active_today = None
        if total_employees and offline_count is not None:
            active_today = max(total_employees - offline_count - on_leave_today, 0)

        return Response(
            {
                "total_employees": total_employees,
                "on_leave_today": on_leave_today,
                "active_today": active_today,
                "joining_today": joining_today,
                "joining_week": joining_week,
                "offline_count": offline_count,
                "online_count": online_count,
                "pending_leave_requests": pending_leave,
            },
            status=200,
        )


class DashboardBirthdaysAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not (
            user.has_perm("employee.view_employee")
            or EmployeeWorkInformation.objects.filter(
                reporting_manager_id=getattr(user, "employee_get", None)
            ).exists()
        ):
            return Response({"error": "Permission denied"}, status=403)

        default_avatar_url = "https://ui-avatars.com/api/?background=random&name="
        birthdays = []
        for emp in birthday():
            department = emp.get_department()
            job_position = emp.get_job_position()
            profile = (
                emp.get_avatar()
                if hasattr(emp, "get_avatar")
                else (
                    f"{default_avatar_url}{emp.employee_first_name}+{emp.employee_last_name}"
                )
            )
            days_until = getattr(emp, "days_until_birthday", 0)
            if days_until == 0:
                days_label = "Today"
            elif days_until == 1:
                days_label = "Tomorrow"
            else:
                days_label = f"In {days_until} days"

            birthdays.append(
                {
                    "id": emp.id,
                    "name": f"{emp.employee_first_name} {emp.employee_last_name}".strip(),
                    "profile": profile,
                    "dob": emp.dob.strftime("%d %b") if emp.dob else "",
                    "days_until_birthday": days_until,
                    "days_label": days_label,
                    "department": department.department if department else "",
                    "job_position": job_position.job_position if job_position else "",
                }
            )

        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(birthdays, request)
        return paginator.get_paginated_response(page)


class DashboardOnLeaveTodayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_manager = EmployeeWorkInformation.objects.filter(
            reporting_manager_id=getattr(user, "employee_get", None)
        ).exists()
        if not (user.has_perm("leave.view_leaverequest") or is_manager):
            return Response({"error": "Permission denied"}, status=403)

        leaves = LeaveRequest.employees_on_leave_today(status="approved")
        data = []
        for leave in leaves.select_related("employee_id", "leave_type_id"):
            employee = leave.employee_id
            profile = employee.employee_profile
            if profile:
                profile = settings.MEDIA_URL + profile
            data.append(
                {
                    "id": leave.id,
                    "employee_id": employee.id,
                    "employee_name": employee.get_full_name(),
                    "employee_profile": profile,
                    "leave_type": (
                        leave.leave_type_id.name if leave.leave_type_id else ""
                    ),
                    "start_date": leave.start_date,
                    "end_date": leave.end_date,
                    "status": leave.status,
                }
            )

        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(data, request)
        return paginator.get_paginated_response(page)


class DashboardWorkInfoPendingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_manager = EmployeeWorkInformation.objects.filter(
            reporting_manager_id=getattr(user, "employee_get", None)
        ).exists()
        if not (
            user.has_perm("employee.view_employeeworkinformation") or is_manager
        ):
            return Response({"error": "Permission denied"}, status=403)

        fields_to_focus = [
            "job_position_id",
            "department_id",
            "work_type_id",
            "employee_type_id",
            "job_role_id",
            "reporting_manager_id",
            "company_id",
            "location",
            "email",
            "mobile",
            "shift_id",
            "date_joining",
            "contract_end_date",
            "basic_salary",
            "salary_hour",
        ]
        search = request.GET.get("search", "")
        employees_with_pending = []
        employees_workinfos = filtersubordinates(
            request,
            queryset=EmployeeWorkInformation.objects.filter(
                employee_id__employee_first_name__icontains=search,
                employee_id__is_active=True,
            ),
            perm="employee.view_employeeworkinformation",
        )
        for work_info in employees_workinfos.select_related("employee_id"):
            completed_field_count = sum(
                1
                for field_name in fields_to_focus
                if getattr(work_info, field_name) is not None
            )
            if completed_field_count < 15:
                employees_with_pending.append(
                    {
                        "employee_id": work_info.employee_id.id,
                        "employee_name": work_info.employee_id.get_full_name(),
                        "completion_percent": round(
                            (completed_field_count / 15) * 100,
                            1,
                        ),
                    }
                )

        emps = filtersubordinatesemployeemodel(
            request,
            Employee.objects.filter(employee_work_info__isnull=True, is_active=True),
            perm="employee.view_employeeworkinformation",
        )
        for emp in emps:
            employees_with_pending.insert(
                0,
                {
                    "employee_id": emp.id,
                    "employee_name": emp.get_full_name(),
                    "completion_percent": 0,
                },
            )

        employees_with_pending.sort(key=lambda item: item["completion_percent"])
        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(employees_with_pending, request)
        return paginator.get_paginated_response(page)
