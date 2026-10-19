from enum import StrEnum


class Perms(StrEnum):
    VIEW_ALL_ORDERS = "acme.view_order"
    VIEW_ALL_ACCOUNTS = "acme.view_account"
    CHANGE_ALL_ACCOUNTS = "acme.change_account"
    EDIT_PREAUTHS = "acme.change_pre_authorized_account_identifier"
    EDIT_USAGE = "acme.change_usage"
    EDIT_TOS = "acme.change_terms_of_service"
