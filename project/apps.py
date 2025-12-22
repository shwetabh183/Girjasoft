from django.apps import AppConfig


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "project"

    def ready(self):
        from django.urls import include, path

        from girjasoft.girjasoft_settings import APP_URLS, APPS
        from girjasoft.urls import urlpatterns

        APPS.append("project")
        urlpatterns.append(
            path("project/", include("project.urls")),
        )
        APP_URLS.append("project.urls")
        super().ready()
