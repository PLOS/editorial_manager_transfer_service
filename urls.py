from django.urls import re_path

from plugins.editorial_manager_transfer_service import views


urlpatterns = [
    re_path(r'^manager/$', views.manager, name='editorial_manager_transfer_service_manager'),
]
