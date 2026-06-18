from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# ──────────────────────────────────────────────────────────────────────────
# FDI TOOTH NUMBERING — shared constants used by models, views, and templates
# ──────────────────────────────────────────────────────────────────────────
UPPER_RIGHT = [18, 17, 16, 15, 14, 13, 12, 11]
UPPER_LEFT = [21, 22, 23, 24, 25, 26, 27, 28]
LOWER_RIGHT = [48, 47, 46, 45, 44, 43, 42, 41]
LOWER_LEFT = [31, 32, 33, 34, 35, 36, 37, 38]
ALL_TEETH = UPPER_RIGHT + UPPER_LEFT + LOWER_RIGHT + LOWER_LEFT

TOOTH_NAMES = {
    11: "Upper Right Central Incisor", 12: "Upper Right Lateral Incisor",
    13: "Upper Right Canine", 14: "Upper Right 1st Premolar",
    15: "Upper Right 2nd Premolar", 16: "Upper Right 1st Molar",
    17: "Upper Right 2nd Molar", 18: "Upper Right 3rd Molar (Wisdom)",
    21: "Upper Left Central Incisor", 22: "Upper Left Lateral Incisor",
    23: "Upper Left Canine", 24: "Upper Left 1st Premolar",
    25: "Upper Left 2nd Premolar", 26: "Upper Left 1st Molar",
    27: "Upper Left 2nd Molar", 28: "Upper Left 3rd Molar (Wisdom)",
    31: "Lower Left Central Incisor", 32: "Lower Left Lateral Incisor",
    33: "Lower Left Canine", 34: "Lower Left 1st Premolar",
    35: "Lower Left 2nd Premolar", 36: "Lower Left 1st Molar",
    37: "Lower Left 2nd Molar", 38: "Lower Left 3rd Molar (Wisdom)",
    41: "Lower Right Central Incisor", 42: "Lower Right Lateral Incisor",
    43: "Lower Right Canine", 44: "Lower Right 1st Premolar",
    45: "Lower Right 2nd Premolar", 46: "Lower Right 1st Molar",
    47: "Lower Right 2nd Molar", 48: "Lower Right 3rd Molar (Wisdom)",
}

# Which anatomical SVG shape to draw for each tooth — used by the chart
# template to pick a <symbol> from the tooth-shapes sprite (central/lateral
# incisors share a shape, canine has its own point, premolars share a
# rounded-cusp shape, 1st/2nd molars share the 4-cusp shape, 3rd molars
# (wisdom) get a slightly squarer 4-cusp variant).
TOOTH_SHAPE = {}
for _n in UPPER_RIGHT + UPPER_LEFT + LOWER_RIGHT + LOWER_LEFT:
    pos = _n % 10  # 1=central incisor .. 8=3rd molar, within each quadrant
    if pos in (1, 2):
        TOOTH_SHAPE[_n] = "incisor"
    elif pos == 3:
        TOOTH_SHAPE[_n] = "canine"
    elif pos in (4, 5):
        TOOTH_SHAPE[_n] = "premolar"
    elif pos in (6, 7):
        TOOTH_SHAPE[_n] = "molar"
    else:
        TOOTH_SHAPE[_n] = "molar3"

CONDITION_CHOICES = [
    ("Healthy", "Healthy"),
    ("Cavity", "Cavity"),
    ("Filled", "Filled"),
    ("Crown", "Crown"),
    ("Root Canal", "Root Canal"),
    ("Extracted", "Extracted"),
    ("Bridge", "Bridge"),
    ("Implant", "Implant"),
    ("Cracked", "Cracked"),
    ("Sensitive", "Sensitive"),
    ("Missing (Congenital)", "Missing (Congenital)"),
    ("Needs Extraction", "Needs Extraction"),
    ("Under Treatment", "Under Treatment"),
]

CONDITION_COLORS = {
    "Healthy": "#4CAF50", "Cavity": "#F44336", "Filled": "#2196F3",
    "Crown": "#9C27B0", "Root Canal": "#FF9800", "Extracted": "#607D8B",
    "Bridge": "#00BCD4", "Implant": "#8BC34A", "Cracked": "#FF5722",
    "Sensitive": "#FFC107", "Missing (Congenital)": "#9E9E9E",
    "Needs Extraction": "#E91E63", "Under Treatment": "#3F51B5",
}


# ──────────────────────────────────────────────────────────────────────────
# TOOTH SURFACES — every tooth is split into 5 clickable/droppable zones.
# Anterior teeth (incisors/canines) use "Incisal" instead of "Occlusal" for
# the biting edge, but we store both under the same SURFACE_CHOICES set and
# let the template pick the right label.
# ──────────────────────────────────────────────────────────────────────────
SURFACE_CHOICES = [
    ("mesial", "Mesial"),
    ("distal", "Distal"),
    ("occlusal", "Occlusal / Incisal"),
    ("buccal", "Buccal / Facial"),
    ("lingual", "Lingual / Palatal"),
]

# Procedures that can be dragged from the palette onto a tooth surface.
# Each entry: code, label, color, icon (single emoji/glyph rendered on the
# surface once applied), and whole_tooth (True = applies the same procedure
# to every surface at once, e.g. an extraction or crown).
PROCEDURE_PALETTE = [
    {"code": "caries",     "label": "Caries / Cavity",   "color": "#F44336", "icon": "●", "whole_tooth": False},
    {"code": "amalgam",    "label": "Amalgam Filling",   "color": "#37474F", "icon": "■", "whole_tooth": False},
    {"code": "composite",  "label": "Composite Filling", "color": "#2196F3", "icon": "■", "whole_tooth": False},
    {"code": "sealant",    "label": "Sealant",           "color": "#26A69A", "icon": "S", "whole_tooth": False},
    {"code": "crown",      "label": "Crown",             "color": "#9C27B0", "icon": "♛", "whole_tooth": True},
    {"code": "root_canal", "label": "Root Canal",        "color": "#FF9800", "icon": "RC", "whole_tooth": True},
    {"code": "extraction", "label": "Extraction",        "color": "#607D8B", "icon": "✕", "whole_tooth": True},
    {"code": "implant",    "label": "Implant",           "color": "#8BC34A", "icon": "I", "whole_tooth": True},
    {"code": "bridge",     "label": "Bridge",             "color": "#00BCD4", "icon": "B", "whole_tooth": True},
    {"code": "fracture",   "label": "Cracked / Fracture", "color": "#FF5722", "icon": "▲", "whole_tooth": False},
    {"code": "watch",      "label": "Watch / Sensitive",  "color": "#FFC107", "icon": "!", "whole_tooth": False},
    {"code": "clear",      "label": "Clear / Healthy",    "color": "#4CAF50", "icon": "", "whole_tooth": False},
]
PROCEDURE_BY_CODE = {p["code"]: p for p in PROCEDURE_PALETTE}


# ──────────────────────────────────────────────────────────────────────────
# STAFF PROFILE — extends Django's built-in User with a clinic role
# ──────────────────────────────────────────────────────────────────────────
class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("dentist", "Dentist"),
        ("receptionist", "Receptionist"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="dentist")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"


# ──────────────────────────────────────────────────────────────────────────
# PATIENT
# ──────────────────────────────────────────────────────────────────────────
class Patient(models.Model):
    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    medical_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)

    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="patients_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("patient_detail", args=[self.pk])

    def tooth_records_by_number(self):
        """Returns {tooth_number: ToothRecord} for fast lookup when rendering the chart."""
        return {r.tooth_number: r for r in self.tooth_records.all()}

    def surface_records_by_tooth(self):
        """Returns {tooth_number: {surface_key: ToothSurfaceRecord}} in two queries total."""
        result = {}
        surfaces = ToothSurfaceRecord.objects.filter(tooth__patient=self).select_related("tooth")
        for s in surfaces:
            result.setdefault(s.tooth.tooth_number, {})[s.surface] = s
        return result


# ──────────────────────────────────────────────────────────────────────────
# TOOTH RECORD — one row per tooth per patient (32 max)
# ──────────────────────────────────────────────────────────────────────────
class ToothRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="tooth_records")
    tooth_number = models.PositiveSmallIntegerField()  # FDI notation, e.g. 11..48
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, default="Healthy")
    treatment = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    recorded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("patient", "tooth_number")
        ordering = ["tooth_number"]

    def __str__(self):
        return f"Tooth #{self.tooth_number} — {self.patient} ({self.condition})"

    @property
    def tooth_name(self):
        return TOOTH_NAMES.get(self.tooth_number, "")

    @property
    def color(self):
        return CONDITION_COLORS.get(self.condition, "#4CAF50")

    def surfaces_by_name(self):
        """Returns {surface_key: ToothSurfaceRecord} for fast template lookup."""
        return {s.surface: s for s in self.surface_records.all()}


# ──────────────────────────────────────────────────────────────────────────
# TOOTH SURFACE RECORD — one row per surface per tooth (5 max per tooth).
# This is what the drag-and-drop chart writes to. ToothRecord above stays
# as the "whole tooth" summary row (used for crowns/extractions/implants
# and the free-text notes box); this table is the fine-grained layer.
# ──────────────────────────────────────────────────────────────────────────
class ToothSurfaceRecord(models.Model):
    tooth = models.ForeignKey(ToothRecord, on_delete=models.CASCADE, related_name="surface_records")
    surface = models.CharField(max_length=10, choices=SURFACE_CHOICES)
    procedure_code = models.CharField(max_length=20, default="clear")
    notes = models.TextField(blank=True)

    recorded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tooth", "surface")
        ordering = ["surface"]

    def __str__(self):
        return f"{self.tooth} — {self.get_surface_display()}: {self.procedure_code}"

    @property
    def procedure(self):
        return PROCEDURE_BY_CODE.get(self.procedure_code, PROCEDURE_BY_CODE["clear"])

    @property
    def color(self):
        return self.procedure["color"]

    @property
    def icon(self):
        return self.procedure["icon"]

    @property
    def label(self):
        return self.procedure["label"]


# ──────────────────────────────────────────────────────────────────────────
# APPOINTMENT
# ──────────────────────────────────────────────────────────────────────────
class Appointment(models.Model):
    STATUS_CHOICES = [
        ("Scheduled", "Scheduled"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
        ("No-show", "No-show"),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    appt_date = models.DateField()
    appt_time = models.TimeField(null=True, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Scheduled")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-appt_date", "-appt_time"]

    def __str__(self):
        return f"{self.patient} — {self.appt_date}"


# ──────────────────────────────────────────────────────────────────────────
# AUDIT LOG — every login, record change, and (optionally) page view
# ──────────────────────────────────────────────────────────────────────────
class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=50)
    details = models.CharField(max_length=500, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-logged_at"]

    def __str__(self):
        who = self.user.username if self.user else "—"
        return f"[{self.logged_at:%Y-%m-%d %H:%M}] {who}: {self.action}"

    @staticmethod
    def log(user, action, details=""):
        AuditLog.objects.create(user=user, action=action, details=details)
