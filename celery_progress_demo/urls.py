from django.contrib import admin
from django.urls import path, include

from download import urls as download_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    # Demo app
    path('', include(download_urls)),
    # Celery progress
    path('celery-progress/', include('celery_progress.urls')),
]