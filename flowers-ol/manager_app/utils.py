import csv

from background_task import background
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.html import strip_tags


def add_message(request, message, tag="info"):
    request.session.setdefault("messages", {})[tag] = message


@background(schedule=0)
def send_delayed_email(to, sender, subject, message_template):
    print("Sending email to {}".format(to))
    send_mail(
        subject=subject,
        html_message=message_template,
        message=strip_tags(message_template),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to],
        fail_silently=False,
    )


@background(schedule=0)
def send_delayed_email_2():
    print("Sending email test")
    send_mail(
        subject="Testing process tasks",
        message="This is a test",
        from_email="noreply-flowers@inria.fr",
        recipient_list=["alexandr.ten@inria.fr", "maxime.adolphe@inria.fr"],
        fail_silently=False,
    )


class ExportCsvMixin:
    """
    Export model as csv
    (Snapshot found in https://readthedocs.org/projects/django-admin-cookbook/downloads/pdf/latest/)
    """

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = "Export Selected"
