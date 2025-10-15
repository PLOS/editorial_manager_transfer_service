__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from django.urls import re_path

from plugins.editorial_manager_transfer_service import views

urlpatterns = [
    re_path(r'^manager/$', views.manager, name='editorial_manager_transfer_service_manager'),
    re_path(r'^logs/$', views.transfer_report, name='editorial_manager_transfer_service_manager_logs'),
    re_path(r"^logs/reports/(?P<report_id>[0-9a-zA-Z-]+)/$", views.transfer_report_logs,
            name="editorial_manager_transfer_service_manager_report_logs"),
    re_path(r"^logs/articles/(?P<article_id>\d+)/reports$", views.transfer_article_reports,
            name="editorial_manager_transfer_service_manager_article_report_logs"),
]
