"""
Send a report about which blacklists have a review date in the past. Distinguishes between enabled
and disabled blacklists
"""

from __future__ import annotations
import datetime

from django.template import Context, Template

from django.conf import settings
from django.core.management import BaseCommand
from django.core.mail import EmailMessage
from geant_argus.blacklist.models import Blacklist

EMAIL_TEMPLATE = """\
The following dashboard blacklist rules are expired and should be reviewed:
{% if enabled|length > 0 %}
[ENABLED]
{% for blacklist in enabled %}({{ blacklist.review_date.isoformat }}) {{ blacklist.name }}
{% endfor %}{% endif %}{% if disabled|length > 0 %}
[DISABLED]
{% for blacklist in disabled %}({{ blacklist.review_date.isoformat }}) {{ blacklist.name }}
{% endfor %}{% endif %}"""
EMAIL_SUBJECT = "summary of expired dashboard blacklist rules"


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_mail_to = getattr(settings, "SEND_EXPIRED_BLACKLISTS_EMAILS_TO", None)
        if not send_mail_to:
            self.stdout.write(
                self.style.WARNING("SEND_EXPIRED_BLACKLISTS_EMAILS_TO not set, not sending report")
            )
            return

        data = self.get_expired_blacklists()
        if not data["count"]:
            self.stdout.write("no expired blackists found")
            return
        self.stdout.write(f"sending report for {data['count']} expired blacklists")
        self.send_report(data, send_mail_to=send_mail_to)

    def get_expired_blacklists(self, today=None):
        today = today or datetime.date.today()
        blacklists = Blacklist.objects.filter(review_date__lte=today).order_by("review_date").all()
        enabled = []
        disabled = []
        for bl in blacklists:
            if bl.enabled:
                enabled.append(bl)
            else:
                disabled.append(bl)
        return {
            "count": len(enabled) + len(disabled),
            "enabled": enabled,
            "disabled": disabled,
        }

    def render_body(self, template_str, context):
        template = Template(template_str)
        return template.render(Context(context))

    def send_report(self, blacklists: dict, send_mail_to):
        body = self.render_body(EMAIL_TEMPLATE, blacklists)
        email = EmailMessage(
            subject=EMAIL_SUBJECT,
            body=body,
            from_email=None,
            to=send_mail_to,
        )
        email.send()
