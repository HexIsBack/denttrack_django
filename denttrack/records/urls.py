from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("patients/", views.patient_list, name="patient_list"),
    path("patients/add/", views.patient_create, name="patient_create"),
    path("patients/<int:pk>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:pk>/edit/", views.patient_edit, name="patient_edit"),
    path("patients/<int:pk>/delete/", views.patient_delete, name="patient_delete"),

    path("patients/<int:pk>/chart/", views.tooth_chart, name="tooth_chart"),
    path("patients/<int:pk>/chart/tooth/<int:tooth_number>/", views.tooth_detail, name="tooth_detail"),
    path("patients/<int:pk>/chart/tooth/<int:tooth_number>/apply/", views.apply_procedure, name="apply_procedure"),

    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/add/", views.appointment_create, name="appointment_create"),

    path("audit-log/", views.audit_log, name="audit_log"),

    path("settings/", views.settings_view, name="settings"),
    path("settings/staff/add/", views.staff_create, name="staff_create"),
    path("settings/staff/<int:pk>/edit/", views.staff_edit, name="staff_edit"),
    path("settings/staff/<int:pk>/toggle/", views.staff_toggle_active, name="staff_toggle"),
]
