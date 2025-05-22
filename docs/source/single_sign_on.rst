.. _single-sign-on:

Single sign on (OIDC)
=====================

Geant Argus supports Single Sign On using ``social-auth-core`` and ``social-auth-django``
(`Python Social Auth <https://python-social-auth.readthedocs.io/en/latest/>`_). These libraries
make integration with CoreAAI straight forward for authentication of users. However, they only
deal with the first part of the auhtentication/authorization flow, namely authentication when
a user logs in. It does not handle authorization neither does it make sure that the authentication
(and authorization) is still valid for an existing session.

CoreAAI
-------

Geant Argus is registered as an OIDC Client in the CoreAAI platform. When registering, the
following authorization grants are required:

 * authorization_code
 * refresh_token

Also, the following scopes are required:

 * Display name
 * Email address
 * Groups (Entitlements)

Development
###########

During development, by default OIDC integration is disabled. To start developing with the Core AAI
OIDC integration, set ``ARGUS_OIDC_DISABLE`` environment variable to 0 (or unset it completely) in
your ``cmd.sh``. You then also need to set the other ``ARGUS_OIDC_*`` environment variables in your
``cmd.sh``. The values for these variables can be found in LastPass under the Argus OIDC settings.

For development, Geant Argus is registered as a different application with a different
``client_id`` than for production. The reason for this is that the development client_id supports
a redirect uri beginning with ``http://127.0.0.1:8000`` so that it can be used with local
development. In order to log in using the development ``client_id`` your oidc user account must be
part of the Sandbox VO group. You can add yourself to this group as part of the login process.

.. _single-sign-on-authorization:

Authorization
-------------

Geant Argus uses group based authentication. By default, OIDC users have read-only access to Argus.
Then, depending on authorization rules, OIDC users can be assigned Argus groups based on their
*entitlements*. Entitlements is the list of VO groups that the user is part of. This list is part
of the user data coming from the CoreAAI platform.

Mapping the entitlements to Argus groups is based on the ``OIDC_AUTHORIZATION_RULES`` setting
which is set using the :ref:`config-json`. This setting contains a list of rules that can have one
of two types. The first is an entitlement rule to one-to-one map an entitlement to a group. For
example::

  {
    "entitlement": "some:entitlement:string",
    "group": "some-group"
  }

The second type is an entitlement pattern to use regex to capture groups from a class of
entitlements an construct a group name based on the result. The named regex capture groups
can be used to form a group name using python ``format`` style string interpolation. For
example::

  {
    "entitlement_pattern": "prefix:(?P<group>\\S+)#aai.geant.org",
    "group": "{group}-members"
  }

The above example would mean that a user with an entitlement ``prefix:swd#aai.geant.org``
would be added to the ``swd-members`` group. Keep in mind that the regex should be constructed
in such a way to prevent accidental matches.

The actual entitlements that users have are URNs and are generally more complex in nature, but the
concept remains the same.

After a user has been assigned groups, these groups are used to determine the permissions a user.
There are currently two groups: ``editors`` and ``admin``. Members of the ``editors`` group have
read-write access, while members of the ``admin`` group also have access to the *admin*
backend.


Middleware
----------

By default, once a user has successfully logged in, Python Social Auth does not validate whether
a user is still active in the OIDC provider or if their entitlements have changed. Geant Argus has
middleware in place that periodically checks the CoreAAI platform for these changes:
``geant_argus.auth.SocialAuthRefreshMiddleware``.

.. note::
  As of May 2025 there is a bug in the CoreAAi platform that prevents the
  ``SocialAuthRefreshMiddleware`` to obtain a user's current entitlements for the duration of the
  user's session. Therefore this middleware has been disabled in favor of a different middleware:
  ``geant_argus.auth.SocialAuthLimitSessionAgeMiddleware``. This middleware limits the session
  lifetime of OIDC users to 24 hours, so that after a user's authorization has been revoked, it
  takes a maximum of 24 hours for the user's sessions to be evicted from Geant Argus. This session
  lifetime was chosen as a compromise between security and usability. It is also possible to delete
  a user's sessions manually through the admin interface, under *Sessions*


Settings
--------

The following settings are used to setup the SSO configuration.

.. list-table::
  :widths: 25 50 25
  :header-rows: 1

  * - Setting
    - Description
    - Location
  * - ``ARGUS_OIDC_DISABLE``
    - Whether to disable the OIDC authentication backend
    - Environment variable
  * - ``ARGUS_OIDC_METHOD_NAME``
    - The text to show on the button in the login page
    - ``geant_argus.settings.base``
  * - ``ARGUS_OIDC_URL``
    - The root url of the CoreAAI OIDC service
    - Environment variable
  * - ``ARGUS_OIDC_CLIENT_ID``
    - The Geant Argus OIDC client ID, see Lastpass
    - Environment variable
  * - ``ARGUS_OIDC_SECRET``
    - The Geant Argus OIDC client secret, see Lastpass
    - ``geant_argus.settings.base``
  * - ``OIDC_AUTHORIZATION_RULES``
    - A list of authorization rules as described in :ref:`single-sign-on-authorization`
    - ``config.json``
  * - ``SOCIAL_AUTH_OIDC_SCOPE``
    - The OIDC scopes to request with the authentication request, in addition to the default
      ``openid`` , ``profile`` and ``email`` scopes. ``entitlements`` is required to obtain the
      entitlements and ``offline_access`` is required for the refresh token
    - ``geant_argus.settings.base``
  * - ``SOCIAL_AUTH_PIPELINE``
    - When a user logs in using OIDC, a pipeline is run to setup the user. See also
      `Python Social Auth: Pipeline <https://python-social-auth.readthedocs.io/en/latest/pipeline.html>`_
    - ``geant_argus.settings.base``
  * - ``SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL``
    - Use the user's email as their username
    - ``geant_argus.settings.base``
  * - ``SOCIAL_AUTH_LOGIN_ERROR_URL``
    - Redirect users back to the login page if an OIDC login errors somehow
    - ``geant_argus.settings.base``
  * - ``SOCIAL_AUTH_JSONFIELD_ENABLED``
    - Optimization to store OIDC data as a JSONField in PostgreSQL
    - ``geant_argus.settings.base``
  * - ``SOCIAL_AUTH_OIDC_AUTH_EXTRA_ARGUMENTS``
    - Addtional parameters to send with the authentication request ``prompt=consent`` is somehow
      required for the ``offline_access`` scope
    - ``geant_argus.settings.base``
