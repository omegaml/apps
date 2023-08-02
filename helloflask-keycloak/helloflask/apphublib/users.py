"""
Copyright (c) one2seven GmbH, makers of omega|ml, http://omegaml.io
"""
import flask
from flask_login import UserMixin, AnonymousUserMixin


class Permission:
    PERMISSIONS = {}

    def __init__(self, permission, groups=None):
        Permission.PERMISSIONS[permission] = self
        self.groups = groups or []

    def allow_for(self, group):
        self.groups.append(group)

    def allowed(self, user):
        return any(g in user.groups for g in self.groups)

    @classmethod
    def get(cls, permission):
        if not Permission.PERMISSIONS:
            Permission.PERMISSIONS.update({
                p: Permission(p, groups=g)
                for p, g in flask.current_app.config.get('APPHUB_PERMISSIONS', {}).items()})
        return Permission.PERMISSIONS.get(permission)


class UserOmegaMixin:
    @property
    def om(self):
        # return the session configuration
        import omegaml as om
        return om.setup()

    def om_for_perm(self, permission):
        # return the configuration for the user
        import omegaml as om
        self: User
        if self.has_perm(permission):
            omega_config = flask.current_app.config.get('APPHUB_PERMISSIONS_OMEGA', {})
            setup_kwargs = omega_config.get(permission, {})
            setup_kwargs.setdefault('make_default', False)
            return om.setup(**setup_kwargs)
        raise ValueError(f'user {self} does not have permission {permission}')


class User(UserOmegaMixin, UserMixin):
    def __init__(self, userid):
        self.id = self.userid = userid
        self._load_claims()

    def _load_claims(self):
        # support for local testing, non-JWT environments
        _all_claims = flask.current_app.config.get('USER_CLAIMS', {})
        _default_claims = _all_claims.get('__default__', {})
        # -- in apphub, login processing will set user.claims to JWT payload
        self.claims = _all_claims.get(self.userid) or _default_claims

    @property
    def groups(self):
        group_claim = flask.current_app.config.get('JWT_GROUPS_ATTRIBUTE', 'groups')
        return self.claims.get(group_claim, [])

    def has_perm(self, permission):
        p = Permission.get(permission)
        return p.allowed(self) if p else False


class AnonymousUser(UserOmegaMixin, AnonymousUserMixin):
    claims = {}
    groups = []
    userid = None

    def has_perm(self, permission):
        return False
