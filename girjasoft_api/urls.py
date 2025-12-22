from django.urls import include, path

urlpatterns = [
    path("auth/", include("girjasoft_api.api_urls.auth.urls")),
    path("asset/", include("girjasoft_api.api_urls.asset.urls")),
    path("base/", include("girjasoft_api.api_urls.base.urls")),
    path("employee/", include("girjasoft_api.api_urls.employee.urls")),
    path("notifications/", include("girjasoft_api.api_urls.notifications.urls")),
    path("payroll/", include("girjasoft_api.api_urls.payroll.urls")),
    path("attendance/", include("girjasoft_api.api_urls.attendance.urls")),
    path("leave/", include("girjasoft_api.api_urls.leave.urls")),
]
