"""
Optional request-level audit hook.

By default this middleware does nothing on every request (page-view logging
gets noisy fast and bloats the audit table). It's kept here, wired into
settings.MIDDLEWARE, so you have a single obvious place to add page-view
tracking later if a clinic ever asks for it — e.g. logging every time a
patient's file is *opened*, not just edited.

Record-level changes (patient added/edited, tooth updated, appointment
booked) are already logged directly in views.py / signals.py, which is the
more useful and far less noisy audit trail for a small clinic.
"""


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
