import pytest

from geant_argus.blacklist.models import Blacklist


@pytest.mark.django_db
def test_no_blacklists_by_default():
    assert len(Blacklist.objects.all()) == 0
