import logging
from typing import Any

import djangosaml2.backends
import inject
from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend as BaseRemoteUserBackend
from django.contrib.auth.models import Group, User
from django.http import HttpRequest

from certificat.settings.dynamic import (
    ApplicationSettings,
    RemoteAuthSettings,
    SAMLAuthSettings,
)
from certificat.utils import coerce_to_list, split_delimited_string

logger = logging.getLogger(__name__)


class RemoteUserBackend(BaseRemoteUserBackend):
    def configure_user(self, request: HttpRequest, user, created=True):
        """
        Configure a user and return the updated user.

        By default, return the user unmodified.
        """
        remote_auth_settings: RemoteAuthSettings = inject.instance(
            ApplicationSettings
        ).authentication

        for header, attributes in remote_auth_settings.attribute_mapping.items():
            attributes = coerce_to_list(attributes)
            if header in request.META:
                for attribute in attributes:
                    try:
                        setattr(user, attribute, request.META[header])
                    except:  # noqa: E722
                        logger.exception(
                            "Error settings attribute %s on user object", attribute
                        )

        if remote_auth_settings.groups_header:
            _sync_user_groups(
                user,
                split_delimited_string(
                    request.META.get(remote_auth_settings.groups_header, ""),
                    remote_auth_settings.groups_header_delimiter,
                ),
            )

        _reconcile_superuser(
            user,
            remote_auth_settings.administrators,
            remote_auth_settings.administrators_groups,
        )
        user.save()

        return user


class Saml2Backend(djangosaml2.backends.Saml2Backend):
    # TODO: should probably override the _extract_user_identifier_params
    # method and namespace the identifier by tenant. This gets a little
    # hairy with discovery because a bad actor could change the tenant
    # identifier and co-opt someone else's username. A lot of service
    # providers will maintain an explicit entity id -> domain relationship
    # and scope users like that.

    def _extract_user_identifier_params(
        self, session_info: dict, attributes: dict, attribute_mapping: dict
    ) -> tuple[str, Any | None]:
        """Returns the attribute to perform a user lookup on, and the value to use for it.
        The value could be the name_id, or any other saml attribute from the request.
        """
        # Lookup key
        user_lookup_key = self._user_lookup_attribute
        if attributes.get("uid") == []:
            del attributes["uid"]

        logger.debug(f"SAML login raw attributes: {attributes}")
        # Lookup value
        if getattr(settings, "SAML_USE_NAME_ID_AS_USERNAME", False):
            if session_info.get("name_id"):
                logger.debug(f"name_id: {session_info['name_id']}")
                user_lookup_value = session_info["name_id"].text
            else:
                logger.error(
                    "The nameid is not available. Cannot find user without a nameid."
                )
                user_lookup_value = None
        else:
            # Obtain the value of the custom attribute to use
            user_lookup_value = self._get_attribute_value(
                user_lookup_key, attributes, attribute_mapping
            )

        return user_lookup_key, self.clean_user_main_attribute(user_lookup_value)

    def _update_user(
        self,
        user: User,
        attributes: dict,
        attribute_mapping: dict,
        force_save: bool = False,
    ):
        """
        Updates user attributes that aren't easily mappable.
        """

        user = super()._update_user(
            user, attributes, attribute_mapping, force_save=force_save
        )

        # Gets a list of all the admins in the config file and gives them access
        # to the backend
        saml_settings = SAMLAuthSettings.get()

        logger.debug("adding groups for user %s", user.username)
        _reconcile_idp_groups(user, attributes)
        _reconcile_superuser(
            user, saml_settings.administrators, saml_settings.administrators_groups
        )

        return user


def _reconcile_superuser(
    user: User, admins: list[str] | None = None, admin_groups: list[str] | None = None
):
    """Grants superuser and Django admin access to configured administrators,
    and takes both away from anyone who is no longer one."""
    admins = admins or []
    admin_groups = admin_groups or []

    normalized_user_group_names = [g.name.lower() for g in user.groups.all()]
    user_in_admin_group = False
    for name in admin_groups:
        if name.lower() in normalized_user_group_names:
            user_in_admin_group = True
            break

    if user.username in admins or user_in_admin_group:
        logger.debug(
            "user %s found in administrators config, granting superuser access",
            user.username,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
    elif user.is_superuser:
        logger.debug(
            "user %s is no longer an administrator, removing superuser access",
            user.username,
        )
        user.is_staff = False
        user.is_superuser = False
        user.save()

    return user


def _sync_user_groups(user: User, group_names: list[str]):
    """Makes the user's Django groups exactly match the groups sent by the
    identity provider. Group names map directly to Django group names, and
    groups that don't exist yet are created. Any group membership not sent by
    the identity provider is removed, including memberships assigned by hand.
    """
    new_group_names = {g for g in group_names if g}

    existing_group_names = set(
        Group.objects.filter(name__in=new_group_names).values_list("name", flat=True)
    )
    for group_name in new_group_names - existing_group_names:
        Group.objects.get_or_create(name=group_name)

    current_group_names = set(user.groups.values_list("name", flat=True))
    logger.debug("removing groups: %s", ",".join(current_group_names - new_group_names))
    logger.debug("adding groups: %s", ",".join(new_group_names - current_group_names))
    user.groups.set(Group.objects.filter(name__in=new_group_names))


def _reconcile_idp_groups(user: User, attributes: dict):
    # TODO: We support discovery, but groups aren't namespaced by tenant.
    # Group mapping should be disabled with discovery or groups should be
    # namespaced somehow by tenant.

    # TODO: assert the authentication type is saml...
    saml_settings: SAMLAuthSettings = inject.instance(
        ApplicationSettings
    ).authentication

    saml_groups = attributes.get(saml_settings.group_attribute, [])
    logger.debug(
        "saml groups from assertion: %s", ",".join(g for g in saml_groups if g)
    )
    _sync_user_groups(user, saml_groups)
