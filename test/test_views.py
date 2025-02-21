import pytest


@pytest.mark.django_db
class TestLoginView:
    def test_login_view_has_geant_aai_option(self, client):
        result = client.get("/accounts/login/")
        assert "Geant Federated Login" in result.content.decode()

    def test_login_shows_privacy_policy(self, client):
        result = client.get("/accounts/login/")
        assert "Privacy Policy" in result.content.decode()
