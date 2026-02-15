from django.urls import path
from . import views

urlpatterns = [
    path("logs/", views.logs_orm_view, name="logs_orm"),
    path("logs/sql/", views.logs_sql_view, name="logs_sql"),
    path("logs/crud-sql/", views.logs_crud_sql_view, name="logs_crud_sql"),
    path("logs/procedure/", views.logs_procedure_view, name="logs_procedure"),
]