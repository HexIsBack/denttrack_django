from django.contrib import admin
from .models import Patient, ToothRecord, ToothSurfaceRecord, Appointment, AuditLog, StaffProfile


class ToothSurfaceInline(admin.TabularInline):
    model = ToothSurfaceRecord
    extra = 0
    fields = ("surface", "procedure_code", "notes", "recorded_by", "recorded_at")
    readonly_fields = ("recorded_at",)


class ToothRecordInline(admin.TabularInline):
    model = ToothRecord
    extra = 0
    fields = ("tooth_number", "condition", "treatment", "notes", "recorded_by", "recorded_at")
    readonly_fields = ("recorded_at",)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "gender", "created_at")
    search_fields = ("first_name", "last_name", "phone", "email")
    list_filter = ("gender",)
    inlines = [ToothRecordInline]


@admin.register(ToothRecord)
class ToothRecordAdmin(admin.ModelAdmin):
    list_display = ("patient", "tooth_number", "condition", "recorded_by", "recorded_at")
    list_filter = ("condition",)
    search_fields = ("patient__first_name", "patient__last_name")
    inlines = [ToothSurfaceInline]


@admin.register(ToothSurfaceRecord)
class ToothSurfaceRecordAdmin(admin.ModelAdmin):
    list_display = ("tooth", "surface", "procedure_code", "recorded_by", "recorded_at")
    list_filter = ("surface", "procedure_code")
    search_fields = ("tooth__patient__first_name", "tooth__patient__last_name")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "dentist", "appt_date", "appt_time", "status")
    list_filter = ("status", "appt_date")
    search_fields = ("patient__first_name", "patient__last_name")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("logged_at", "user", "action", "details")
    list_filter = ("action",)
    readonly_fields = ("user", "action", "details", "logged_at")

    def has_add_permission(self, request):
        return False  # audit entries are created by the system, not typed in manually


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
