from social_core.exceptions import AuthFailed


def require_existing_user(backend, user=None, *args, **kwargs):
    if not user:
        raise AuthFailed(backend, "You are not allowed to access this application")


def get_userdata(backend, response, **kwargs):
    print(response)
