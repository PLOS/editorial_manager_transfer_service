__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from django.urls import re_path

from plugins.editorial_manager_transfer_service import views


urlpatterns = [
    re_path(r'^manager/$', views.manager, name='editorial_manager_transfer_service_manager'),
]
