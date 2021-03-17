from django.urls import path
# Demo view
from .views import demo_view

app_name = 'download'

urlpatterns = [
	# Demo view
	path('', demo_view, name='demo'),
]