import pytest

from geant_argus.blacklist.models import Blacklist
from django.conf import settings


@pytest.mark.django_db
def test_no_blacklists():
    settings
    assert len(Blacklist.objects.all()) == 0
