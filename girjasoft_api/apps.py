from django.apps import AppConfig


class GirjasoftApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "girjasoft_api"

    def ready(self):
        from django.urls import include, path

        from girjasoft.urls import urlpatterns

        urlpatterns.append(
            path("api/", include("girjasoft_api.urls")),
        )
        super().ready()
