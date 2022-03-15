# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Registry and definition of community roles."""


from dataclasses import dataclass, field


@dataclass(frozen=True)
class Role:
    """Role class"""

    name: str = ''
    """Name of the role."""

    title: str = ''
    """Title of the role."""

    description: str = ''
    """Brief description of capabilities of the role."""

    can_manage_roles: list = field(default_factory=list)
    """List of other roles that this role can manage."""

    is_owner: bool = False
    """This role is the owner role (only one can exists)."""

    def can_manage(self, role_name):
        """Determine if this role can manage the role name."""
        return role_name in self.can_manage_roles

    def __hash__(self):
        """Compute a hash for use with e.g. sets"""
        return self.name.__hash__()


class RoleRegistry:
    """Registry of community roles."""

    def __init__(self, roles_definitions):
        """Initialize the role registry."""
        self._roles = {
            name: Role(name=name, **data)
            for (name, data) in roles_definitions.items()
        }
        self._owner = None
        for r in self._roles.values():
            if r.is_owner:
                assert self._owner is None, \
                        "Only one role be defined as owner."
                self._owner = r
        assert self._owner is not None, "One role must be defined as owner."

    def __contains__(self, key):
        """Determine if key is a valid role id."""
        return key in self._roles

    def __getitem__(self, key):
        """Get a role for a specific key."""
        return self._roles[key]

    def __iter__(self):
        """Iterate list of roles."""
        return iter(self.roles)

    @property
    def roles(self):
        """Get a list of roles"""
        return self._roles.values()

    @property
    def owner_role(self):
        """Get the owner role"""
        return self._owner

    def manager_roles(self, role_name):
        """Get all roles that can manage members a given role.

        A manager can manage other manages, curators and readers.
        An owner can manage other owners, managers, curators and readers.

        This is used for instance to ensure that a manager cannot invite an
        owner and thereby escalate their privileges.
        """
        allowed_roles = []

        for role in self.roles:
            if role.can_manage(role_name):
                allowed_roles.append(role)
        return allowed_roles
