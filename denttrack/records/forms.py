from django import forms
from django.contrib.auth.models import User

from .models import Patient, ToothRecord, ToothSurfaceRecord, Appointment, StaffProfile


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "first_name", "last_name", "birthdate", "gender",
            "phone", "email", "address", "medical_history", "allergies",
        ]
        widgets = {
            "birthdate": forms.DateInput(attrs={"type": "date"}),
            "medical_history": forms.Textarea(attrs={"rows": 3}),
            "allergies": forms.Textarea(attrs={"rows": 2}),
            "address": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ToothRecordForm(forms.ModelForm):
    class Meta:
        model = ToothRecord
        fields = ["condition", "treatment", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ToothSurfaceRecordForm(forms.ModelForm):
    class Meta:
        model = ToothSurfaceRecord
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "dentist", "appt_date", "appt_time", "purpose", "status", "notes"]
        widgets = {
            "appt_date": forms.DateInput(attrs={"type": "date"}),
            "appt_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        # Only show dentist/admin accounts in the dentist dropdown
        self.fields["dentist"].queryset = User.objects.filter(profile__role__in=["dentist", "admin"])


class StaffCreateForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="Full Name")
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    role = forms.ChoiceField(choices=StaffProfile.ROLE_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get("password")
        cpw = cleaned.get("confirm_password")
        if pw and cpw and pw != cpw:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username


class PatientSearchForm(forms.Form):
    q = forms.CharField(required=False, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Search by name or phone…"}))
