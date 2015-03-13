## Modifications, customizations, workarounds, and decisions for external modules and code

### django-oauth-toolkit

#### no support for access token in the query string

I added middleware that takes an access token in the query string and applies
it as an `Authorization: Bearer` header.

### django-user-accounts

#### minimum password length

A minimum password length is not enforced, causing us to subclass:

- `SignupForm`
- `ChangePasswordForm`
- `PasswordResetTokenForm`

There's an [open pull
request](https://github.com/pinax/django-user-accounts/pull/155/files) from
November, 2014 (but it only changes `SignupForm`).

#### sites dependency

We've pinned to a fork of django-user-accounts to avoid a dependency on
django.contrib.sites.
