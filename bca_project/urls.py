
from django.contrib import admin
from django.urls import path ,include
from django.conf.urls.static import static
from django.conf import settings
from project_app.admin import flavorcraft_admin_site

urlpatterns = [
    path('admin/', flavorcraft_admin_site.urls),
    path("",include('project_app.urls'))

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
