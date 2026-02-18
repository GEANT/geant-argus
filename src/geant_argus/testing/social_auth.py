from social_core.backends.open_id_connect import OpenIdConnectAuth


class FakeOpenIDConnectAuth(OpenIdConnectAuth):
    entitlements = ()

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

    # No idea how this stuff works but this signature needed fixing due to a breaking change.
    # Seems like it shouldnt cause any trouble after doing some investigation.
    # Breaking change at line 52:
    # https://github.com/python-social-auth/social-core/commit/bb7ba282f5784f0eef79473253f46f1e8cf33433
    def extra_data(self, user, uid, response, *args):
        return {**response, "extra": "data"}

    def user_data(self, access_token, *args, **kwargs):
        return {"entitlements": list(self.entitlements)}

    def request(self, url, method="GET", *args, **kwargs):
        raise RuntimeError(
            "Cannot make a http request in during testing, add additional methods to "
            "FakeOpenIDConnectAuth to prevent making actual requests"
        )
