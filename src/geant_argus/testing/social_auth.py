from social_core.backends.open_id_connect import OpenIdConnectAuth


class FakeOpenIDConnectAuth(OpenIdConnectAuth):
    def oidc_config(self):
        return {
            "token_endpoint_auth_methods_supported": True,
            "userinfo_endpoint": "user_info",
            "authorization_endpoint": "/authorization",
            "token_endpoint": "/token",
            "revocation_endpoint": "/revocation",
            "issuer": "issuer",
        }

    def refresh_token(self, token, *args, **kwargs):
        return {"auth_token": "auth-token", "refresh_token": "refresh-token"}

    def extra_data(self, user, uid, response, extra_data):
        return {**response, "extra": "data"}

    def user_data(self, access_token, *args, **kwargs):
        return {"entitlements": ["some-entitlement"]}

    def request(self, url, method="GET", *args, **kwargs):
        raise RuntimeError(
            "Cannot make a http request in during testing, add additional methods to "
            "FakeOpenIDConnectAuth to prevent making actual requests"
        )
