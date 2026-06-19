import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import PatientForm, ToothRecordForm, ToothSurfaceRecordForm, AppointmentForm, StaffCreateForm, StaffEditForm, PatientSearchForm
from .models import (
    Patient, ToothRecord, ToothSurfaceRecord, Appointment, AuditLog,
    UPPER_RIGHT, UPPER_LEFT, LOWER_RIGHT, LOWER_LEFT, TOOTH_NAMES, CONDITION_COLORS,
    TOOTH_SHAPE, SURFACE_CHOICES, PROCEDURE_PALETTE, PROCEDURE_BY_CODE,
)
from .tooth_shapes import get_tooth_geometry


def is_admin(user):
    return hasattr(user, "profile") and user.profile.role == "admin"


# ──────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    context = {
        "patient_count": Patient.objects.count(),
        "tooth_record_count": ToothRecord.objects.count(),
        "upcoming_count": Appointment.objects.filter(status="Scheduled").count(),
        "staff_count": User.objects.filter(is_active=True).count(),
        "recent_patients": Patient.objects.order_by("-created_at")[:10],
    }
    return render(request, "records/dashboard.html", context)


# ──────────────────────────────────────────────────────────────────────────
# PATIENTS
# ──────────────────────────────────────────────────────────────────────────
@login_required
def patient_list(request):
    form = PatientSearchForm(request.GET or None)
    patients = Patient.objects.all()
    q = ""
    if form.is_valid():
        q = form.cleaned_data.get("q", "").strip()
        if q:
            patients = patients.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(phone__icontains=q)
            )
    return render(request, "records/patient_list.html", {"patients": patients, "form": form, "q": q})


@login_required
def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            AuditLog.log(request.user, "ADD_PATIENT", f"Patient ID {patient.id}: {patient}")
            messages.success(request, f"Patient '{patient}' added successfully.")
            return redirect("patient_list")
    else:
        form = PatientForm()
    return render(request, "records/patient_form.html", {"form": form, "title": "Add New Patient"})


@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            AuditLog.log(request.user, "UPDATE_PATIENT", f"Patient ID {patient.id}")
            messages.success(request, f"Patient '{patient}' updated.")
            return redirect("patient_list")
    else:
        form = PatientForm(instance=patient)
    return render(request, "records/patient_form.html", {"form": form, "title": f"Edit {patient}"})


@login_required
@user_passes_test(is_admin)
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        name = str(patient)
        pid = patient.id
        patient.delete()
        AuditLog.log(request.user, "DELETE_PATIENT", f"Patient ID {pid} ({name}) deleted")
        messages.success(request, f"Patient '{name}' deleted.")
        return redirect("patient_list")
    return render(request, "records/patient_confirm_delete.html", {"patient": patient})


@login_required
def patient_detail(request, pk):
    """Full record: personal info + tooth summary + appointment history."""
    patient = get_object_or_404(Patient, pk=pk)
    tooth_records = patient.tooth_records.all().order_by("tooth_number")
    appointments = patient.appointments.select_related("dentist").all()
    return render(request, "records/patient_detail.html", {
        "patient": patient,
        "tooth_records": tooth_records,
        "appointments": appointments,
    })


# ──────────────────────────────────────────────────────────────────────────
# TOOTH CHART — the clickable/droppable SVG diagram
# ──────────────────────────────────────────────────────────────────────────
@login_required
def tooth_chart(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    records_by_number = patient.tooth_records_by_number()
    surfaces_by_tooth = patient.surface_records_by_tooth()

    # Layout constants — box size matches tooth_shapes.py's local coordinate
    # system (40 wide x 56 tall) so each tooth's <g transform="translate(x,y)">
    # lines up exactly with its outline/root/surface-band paths.
    TOOTH_W, TOOTH_H, GAP = 40, 56, 10
    upper_row = UPPER_RIGHT + UPPER_LEFT   # 16 teeth, left-to-right on screen
    lower_row = LOWER_RIGHT + LOWER_LEFT   # 16 teeth, left-to-right on screen
    upper_y = 40
    lower_y = upper_y + TOOTH_H + 50

    def build_row(numbers, y, arch):
        row = []
        for i, n in enumerate(numbers):
            rec = records_by_number.get(n)
            tooth_surfaces = surfaces_by_tooth.get(n, {})
            shape = TOOTH_SHAPE.get(n, "molar")
            geo = get_tooth_geometry(shape, arch)

            # Icon label anchor points for each surface — placed by hand
            # per zone so the glyph sits inside its region instead of
            # defaulting to the tooth center for all 5 (which would stack
            # every icon on top of each other).
            crown_mid_y = (geo["crown_top"] + geo["crown_bot"]) / 2
            third_w = geo["box_w"] / 3
            icon_pos = {
                "mesial": (third_w / 2, crown_mid_y),
                "distal": (geo["box_w"] - third_w / 2, crown_mid_y),
                "occlusal": (geo["box_w"] / 2, geo["crown_top"] + (geo["crown_bot"] - geo["crown_top"]) * 0.28),
                "lingual": (geo["box_w"] / 2, crown_mid_y),
                "buccal": (geo["box_w"] / 2, geo["crown_bot"] - (geo["crown_bot"] - geo["crown_top"]) * 0.14),
            }

            surfaces_ordered = []
            for skey in geo["draw_order"]:
                slabel = dict(SURFACE_CHOICES)[skey]
                srec = tooth_surfaces.get(skey)
                ix, iy = icon_pos[skey]
                surfaces_ordered.append({
                    "key": skey,
                    "label": slabel,
                    "path": geo["surface_paths"][skey],
                    "code": srec.procedure_code if srec else "clear",
                    "color": srec.color if srec else PROCEDURE_BY_CODE["clear"]["color"],
                    "icon": srec.icon if srec else "",
                    "proc_label": srec.label if srec else "Healthy",
                    "icon_x": round(ix, 1),
                    "icon_y": round(iy, 1),
                })

            row.append({
                "number": n,
                "name": TOOTH_NAMES.get(n, ""),
                "shape": shape,
                "arch": arch,  # "upper" or "lower" — flips the SVG symbol vertically
                "condition": rec.condition if rec else "Healthy",
                "color": rec.color if rec else CONDITION_COLORS["Healthy"],
                "has_record": rec is not None,
                "surfaces_ordered": surfaces_ordered,
                "outline": geo["outline"],
                "root": geo["root"],
                "box_w": geo["box_w"],
                "box_h": geo["box_h"],
                "half_box_w": geo["box_w"] / 2,
                "crown_top": geo["crown_top"],
                "crown_bot": geo["crown_bot"],
                "third_x1": geo["third_x1"],
                "third_x2": geo["third_x2"],
                "rim": geo["rim"],
                "lingual_w": geo["lingual_w"],
                "lingual_h": geo["lingual_h"],
                "x": i * (TOOTH_W + GAP),
                "y": y,
            })
        return row

    teeth = build_row(upper_row, upper_y, "upper") + build_row(lower_row, lower_y, "lower")
    svg_width = 16 * TOOTH_W + 15 * GAP
    svg_height = lower_y + TOOTH_H + 40
    mid_x = 8 * (TOOTH_W + GAP) - GAP // 2

    return render(request, "records/tooth_chart.html", {
        "patient": patient,
        "teeth": teeth,
        "condition_colors": CONDITION_COLORS,
        "procedure_palette": PROCEDURE_PALETTE,
        "tooth_w": TOOTH_W,
        "tooth_h": TOOTH_H,
        "svg_width": svg_width,
        "svg_height": svg_height,
        "mid_x": mid_x,
        "upper_label_y": upper_y - 16,
        "lower_label_y": lower_y + TOOTH_H + 24,
    })


@login_required
@require_POST
def apply_procedure(request, pk, tooth_number):
    """
    Called by the drag-and-drop chart when a procedure icon is dropped onto
    a tooth surface (or onto the whole tooth, for crowns/extractions/etc).
    Expects JSON body: {"surface": "mesial", "procedure_code": "caries"}
    or {"whole_tooth": true, "procedure_code": "extraction"}.
    Returns JSON so the frontend can repaint just that tooth without a
    full page reload.
    """
    patient = get_object_or_404(Patient, pk=pk)
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON body."}, status=400)

    procedure_code = payload.get("procedure_code")
    if procedure_code not in PROCEDURE_BY_CODE:
        return JsonResponse({"ok": False, "error": "Unknown procedure code."}, status=400)

    tooth_record, _ = ToothRecord.objects.get_or_create(
        patient=patient, tooth_number=tooth_number,
        defaults={"condition": "Healthy", "recorded_by": request.user},
    )

    procedure = PROCEDURE_BY_CODE[procedure_code]
    whole_tooth = payload.get("whole_tooth") or procedure.get("whole_tooth")

    surfaces_touched = []
    if whole_tooth:
        for skey, _slabel in SURFACE_CHOICES:
            srec, _ = ToothSurfaceRecord.objects.update_or_create(
                tooth=tooth_record, surface=skey,
                defaults={"procedure_code": procedure_code, "recorded_by": request.user},
            )
            surfaces_touched.append(skey)
        # Whole-tooth procedures (crown, extraction, implant, bridge, root canal)
        # also drive the summary condition shown elsewhere in the app.
        condition_map = {
            "crown": "Crown", "extraction": "Extracted", "implant": "Implant",
            "bridge": "Bridge", "root_canal": "Root Canal",
        }
        if procedure_code in condition_map:
            tooth_record.condition = condition_map[procedure_code]
            tooth_record.recorded_by = request.user
            tooth_record.save()
    else:
        surface = payload.get("surface")
        valid_surfaces = {s for s, _ in SURFACE_CHOICES}
        if surface not in valid_surfaces:
            return JsonResponse({"ok": False, "error": "Missing or invalid surface."}, status=400)
        ToothSurfaceRecord.objects.update_or_create(
            tooth=tooth_record, surface=surface,
            defaults={"procedure_code": procedure_code, "recorded_by": request.user},
        )
        surfaces_touched.append(surface)

    AuditLog.log(
        request.user, "APPLY_PROCEDURE",
        f"Patient {patient.id} Tooth #{tooth_number}: {procedure['label']} "
        f"({'whole tooth' if whole_tooth else surfaces_touched[0]})"
    )

    return JsonResponse({
        "ok": True,
        "tooth_number": tooth_number,
        "whole_tooth": bool(whole_tooth),
        "surfaces": surfaces_touched,
        "color": procedure["color"],
        "icon": procedure["icon"],
        "label": procedure["label"],
        "tooth_condition": tooth_record.condition,
        "tooth_color": tooth_record.color,
    })


@login_required
def tooth_detail(request, pk, tooth_number):
    """
    Returns the edit panel for a single tooth (used inside the tooth chart page).
    GET  → shows the current condition/treatment/notes for that tooth, plus
           the per-surface procedure breakdown (read from drag-and-drop data).
    POST → saves the whole-tooth condition/treatment/notes changes. For AJAX
            requests (the normal flow from the chart page), responds with
            the same partial so fetch() can swap it straight into the detail
            panel without a full page reload.
    """
    patient = get_object_or_404(Patient, pk=pk)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    just_saved = False

    tooth_record, created = ToothRecord.objects.get_or_create(
        patient=patient, tooth_number=tooth_number,
        defaults={"condition": "Healthy", "recorded_by": request.user},
    )

    if request.method == "POST":
        form = ToothRecordForm(request.POST, instance=tooth_record)
        if form.is_valid():
            tooth_record = form.save(commit=False)
            tooth_record.recorded_by = request.user
            tooth_record.save()
            AuditLog.log(
                request.user, "UPDATE_TOOTH",
                f"Patient {patient.id} Tooth #{tooth_number} → {tooth_record.condition}"
            )
            just_saved = True
            if not is_ajax:
                messages.success(request, f"Tooth #{tooth_number} updated.")
                return redirect("tooth_chart", pk=patient.pk)
    else:
        form = ToothRecordForm(instance=tooth_record)

    existing_surfaces = tooth_record.surfaces_by_name()
    surface_rows = []
    for skey, slabel in SURFACE_CHOICES:
        srec = existing_surfaces.get(skey)
        surface_rows.append({
            "key": skey,
            "label": slabel,
            "procedure_label": srec.label if srec else "Healthy",
            "color": srec.color if srec else PROCEDURE_BY_CODE["clear"]["color"],
            "notes": srec.notes if srec else "",
        })

    context = {
        "patient": patient,
        "tooth_number": tooth_number,
        "tooth_name": TOOTH_NAMES.get(tooth_number, ""),
        "form": form,
        "tooth_record": tooth_record,
        "surface_rows": surface_rows,
        "just_saved": just_saved,
    }

    template = "records/_tooth_detail_panel.html" if is_ajax else "records/tooth_detail.html"
    return render(request, template, context)


# ──────────────────────────────────────────────────────────────────────────
# APPOINTMENTS
# ──────────────────────────────────────────────────────────────────────────
@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related("patient", "dentist").all()
    return render(request, "records/appointment_list.html", {"appointments": appointments})


@login_required
def appointment_create(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save()
            AuditLog.log(request.user, "ADD_APPOINTMENT", f"Patient {appt.patient_id} on {appt.appt_date}")
            messages.success(request, "Appointment scheduled.")
            return redirect("appointment_list")
    else:
        initial = {}
        patient_id = request.GET.get("patient")
        if patient_id:
            initial["patient"] = patient_id
        form = AppointmentForm(initial=initial)
    return render(request, "records/appointment_form.html", {"form": form})


# ──────────────────────────────────────────────────────────────────────────
# AUDIT LOG
# ──────────────────────────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def audit_log(request):
    logs = AuditLog.objects.select_related("user").all()[:500]
    return render(request, "records/audit_log.html", {"logs": logs})


# ──────────────────────────────────────────────────────────────────────────
# SETTINGS
# ──────────────────────────────────────────────────────────────────────────
@login_required
def settings_view(request):
    pw_form = PasswordChangeForm(user=request.user)
    if request.method == "POST" and "change_password" in request.POST:
        pw_form = PasswordChangeForm(user=request.user, data=request.POST)
        if pw_form.is_valid():
            user = pw_form.save()
            update_session_auth_hash(request, user)  # keep the user logged in
            AuditLog.log(request.user, "CHANGE_PASSWORD", "Password changed")
            messages.success(request, "Password changed successfully.")
            return redirect("settings")

    staff = User.objects.select_related("profile").all() if is_admin(request.user) else None
    return render(request, "records/settings.html", {
        "pw_form": pw_form,
        "staff": staff,
        "is_admin_user": is_admin(request.user),
    })


@login_required
@user_passes_test(is_admin)
def staff_create(request):
    if request.method == "POST":
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["role"]
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["full_name"],
                is_superuser=(role == "admin"),
                is_staff=(role == "admin"),
            )
            # The post_save signal in signals.py already created a StaffProfile
            # (role defaults to "admin" if is_superuser else "dentist") — update
            # it here in case the admin picked "receptionist" or something that
            # doesn't match that default.
            user.profile.role = role
            user.profile.save()
            AuditLog.log(request.user, "ADD_DENTIST", f"Added user '{user.username}' as {role}")
            messages.success(request, f"User '{user.username}' added.")
            return redirect("settings")
    else:
        form = StaffCreateForm()
    return render(request, "records/staff_form.html", {"form": form, "action": "Add"})


@login_required
@user_passes_test(is_admin)
def staff_edit(request, pk):
    """Admin changes a staff member's full name, role, or active status."""
    target = get_object_or_404(User, pk=pk)

    # Prevent the only admin from demoting or deactivating themselves.
    if target == request.user and request.method == "POST":
        new_role = request.POST.get("role")
        new_active = request.POST.get("is_active")
        admin_count = User.objects.filter(profile__role="admin", is_active=True).count()
        if new_role != "admin" and admin_count <= 1:
            messages.error(request, "Cannot demote the only administrator account.")
            return redirect("staff_edit", pk=pk)
        if not new_active and admin_count <= 1:
            messages.error(request, "Cannot deactivate the only administrator account.")
            return redirect("staff_edit", pk=pk)

    if request.method == "POST":
        form = StaffEditForm(request.POST)
        if form.is_valid():
            old_role = target.profile.role
            new_role = form.cleaned_data["role"]
            target.first_name = form.cleaned_data["full_name"]
            target.is_active = form.cleaned_data["is_active"]
            target.is_superuser = (new_role == "admin")
            target.is_staff = (new_role == "admin")
            target.save()
            target.profile.role = new_role
            target.profile.save()
            AuditLog.log(
                request.user, "EDIT_STAFF",
                f"Updated '{target.username}': role {old_role}→{new_role}, "
                f"active={target.is_active}"
            )
            messages.success(request, f"'{target.username}' updated.")
            return redirect("settings")
    else:
        form = StaffEditForm(initial={
            "full_name": target.first_name,
            "role": getattr(target, "profile", None) and target.profile.role or "dentist",
            "is_active": target.is_active,
        })

    return render(request, "records/staff_edit_form.html", {
        "form": form,
        "target": target,
    })


@login_required
@user_passes_test(is_admin)
def staff_toggle_active(request, pk):
    """Quick-toggle: deactivate or reactivate a staff account from the table."""
    target = get_object_or_404(User, pk=pk)

    if target == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("settings")

    if target.is_active:
        admin_count = User.objects.filter(profile__role="admin", is_active=True).count()
        if target.profile.role == "admin" and admin_count <= 1:
            messages.error(request, "Cannot deactivate the only administrator account.")
            return redirect("settings")

    target.is_active = not target.is_active
    target.save()
    action = "activated" if target.is_active else "deactivated"
    AuditLog.log(request.user, "TOGGLE_STAFF", f"Account '{target.username}' {action}")
    messages.success(request, f"Account '{target.username}' {action}.")
    return redirect("settings")
