from django.apps import AppConfig


class BackupConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "girjasoft_backup"

    def ready(self):
        from django.urls import include, path

        from girjasoft.urls import urlpatterns

        urlpatterns.append(
            path("backup/", include("girjasoft_backup.urls")),
        )
        super().ready()
