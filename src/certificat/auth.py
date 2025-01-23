from typing import Tuple, Optional, Any
import djangosaml2.backends
from django.contrib.auth.models import Group, User
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class Saml2Backend(djangosaml2.backends.Saml2Backend):
    def _extract_user_identifier_params(
        self, session_info: dict, attributes: dict, attribute_mapping: dict
    ) -> Tuple[str, Optional[Any]]:
        """Returns the attribute to perform a user lookup on, and the value to use for it.
        The value could be the name_id, or any other saml attribute from the request.
        """
        # Lookup key
        user_lookup_key = self._user_lookup_attribute

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
        from certificat.settings.saml import saml_settings

        # Adds the saml group prefix to an array of strings
        def _prefix_groups(groups):
            return [f"{saml_settings.group_sync_prefix} {g}" for g in groups]

        # Gets a list of all the admins in the config file and gives them access
        # to the backend

        logger.debug("adding groups for user " + user.username)

        if user.username in saml_settings.administrators:
            user.is_staff = True
            user.is_superuser = True
            force_save = True

        user = super()._update_user(user, attributes, attribute_mapping, force_save)

        new_saml_group_names = set(
            _prefix_groups(attributes.get(saml_settings.group_attribute, []))
        )

        logger.debug("saml groups: " + ",".join(new_saml_group_names))

        # Gets a list of the current user's groups that begin with the
        # SAML_GROUP_PREFIX, so we don't update any groups set outside this.
        current_user_saml_group_names = set(
            user.groups.filter(
                name__startswith=saml_settings.group_attribute
            ).values_list("name", flat=True)
        )
        # SAML groups existing in the Django database
        existing_saml_groups_lookup = {
            g.name: g for g in Group.objects.filter(name__in=new_saml_group_names)
        }

        # These groups need to be added to the database
        group_names_to_add = new_saml_group_names - existing_saml_groups_lookup.keys()
        # These groups need to be added to the user
        user_groups_to_add = new_saml_group_names - current_user_saml_group_names
        # These groups need to be removed from the user
        user_groups_to_remove = current_user_saml_group_names - new_saml_group_names

        for group_name in group_names_to_add:
            Group.objects.get_or_create(name=group_name)

        user.groups.remove(*Group.objects.filter(name__in=user_groups_to_remove))
        user.groups.add(*Group.objects.filter(name__in=user_groups_to_add))

        return user
