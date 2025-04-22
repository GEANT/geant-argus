import datetime
import pytest
from django.core import mail
from django.core.management import call_command

from geant_argus.blacklist.models import Blacklist, Filter


@pytest.mark.django_db
def test_render_email_body(default_user):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)

    filter = Filter.objects.create(user=default_user, name="some-filter")
    blacklist_params = [
        {"name": "expired-enabled", "enabled": True, "review_date": yesterday},
        {"name": "expired-enabled2", "enabled": True, "review_date": today},
        {"name": "expired-disabled", "enabled": False, "review_date": yesterday},
        {"name": "expired-disabled2", "enabled": False, "review_date": today},
        {"name": "not-expired", "enabled": True, "review_date": tomorrow},
    ]
    for params in blacklist_params:
        Blacklist.objects.create(
            user=default_user, filter=filter, message="some message", **params
        )

    call_command("expiredblacklistsreport")

    # during testing, django automatically switches to the locmem email backend which writes
    # email messages to mail.outbox.
    # cf. https://docs.djangoproject.com/en/5.2/topics/testing/tools/#topics-testing-email
    message = mail.outbox[0]
    assert message.subject == "summary of expired dashboard blacklist rules"

    expected_body = f"""\
The following dashboard blacklist rules are expired and should be reviewed:

[ENABLED]
({yesterday.isoformat()}) expired-enabled
({today.isoformat()}) expired-enabled2

[DISABLED]
({yesterday.isoformat()}) expired-disabled
({today.isoformat()}) expired-disabled2
"""
    assert message.body == expected_body
