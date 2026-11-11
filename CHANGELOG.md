# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses modified [Calendar Versioning](https://calver.org/). 

## Unreleased / In Development

- Centralized and reworked permissions to make permissions apply more consistantly and to separate logical operations from implementation.
- Hundreds of documentation updates to attempt to bring parity to documentation and features.
- Consolidated and reworked ACME finalizer to make the finalizer flow more straightforward.
- Trimmed down the CERTINextACMEFinalizer to reuse code from the ACME finalizer where appropriate.
- Added `order.post-answer-challenges` webhook.
- **Breaking:** Changed `type` key and configuration for ACME finalizer webhook.
- **Breaking:** groups synced from SAML or remote auth are no longer prefixed (e.g. `SAML/admins` is now `admins`) and map directly to Django groups. Migration `acme.0020_remove_group_prefixes` renames existing groups, merging users, permissions and account access into an existing group of the same name
- **Breaking:** the identity provider now owns all group membership. On login, a user's Django groups are replaced with exactly the groups sent by SAML or the remote groups header, so memberships assigned by hand are removed
- Deprecated the `group_sync_prefix` authentication setting (now ignored) and `certificat.utils.PREFIXED_GROUP_REGEX` / `unprefix_group`
- Added an administration page at `/admin/` with links to management tools, a setup checklist and health checks (task worker and stuck orders). It is visible to superusers and anyone with permission to view users or edit the terms of service or usage page
- **Breaking:** moved the Django admin from `/admin/` to `/admin/backend/`
- Added group management at `/admin/groups/`. Groups can be searched and viewed by users with `auth.view_user`; superusers can choose each group's permissions from checkboxes grouped by function (Users, Accounts & Orders, Documentation)
- Added user management at `/admin/users/`. Users with `auth.view_user` can list, search and view user profiles, including each permission and the groups that grant it. Permissions are only granted through groups, not directly to users, and permissions assigned directly to a user in the Django admin are not shown
- Fixed administrators removed from the `administrators` / `administrators_groups` settings keeping access to the Django admin (`is_staff`) after losing superuser
- Fixed list pages returning a server error when the `page` query parameter isn't a number
- The task worker heartbeat now records its last check-in in the database so the web UI can report worker health
- Fixed `EDIT_PREAUTHS` and `EDIT_TOS` permission names, which did not match the Django permission codenames and so were never granted to non-superusers
- Adding postgres support for Huey tasks admin
- Reorganize views to pull business and query logic to external services
- Added links to view all recent orders and all certificates
- Moved to using individual permissions rather than superuser for everything
- Added owner to account bindings and migrated creators to seed owners
- Added orders view
- Adding beta event notifications for certificate creation
- Added readonly to Lit elements that require backend permissions
- Added lego client instructions (thanks @jxscad-rit)
- Added the acme.mask_account_update flag to allow CertifiCat to generate valid responses to account updates

## [2026.8.3] - 2026-08-03

### Added

- Redirect KID URLs to the account page
- mkdocs documentation hosted at https://rit-its.github.io/CertifiCat/
- `start` command for docker build that spawns the web ui and task runner
- certinext-acme finalizer

## [2026.8.2] - 2026-08-01

### Fixed

- Fixed ssl database option lookup for Huey stats connection

- Changing ACME finalizer to verify all nameservers for presence of DNS-01 token before submitting order to upstream

## [2026.8.2] - 2026-08-01

### Fixed

- Fixed ssl database option lookup for Huey stats connection

## [2026.8.1] - 2026-08-01

### Added

- Changed pyproject version to 0.0.0 to better identify manual installations since versioning happens at build time and is derived by tags, not the checked-in pyproject file
- Added support for multiple configured finalizers through the alternative_finalizers setting
- Added webhook base class based on https://www.standardwebhooks.com/ implementation
- Added finalizer field to accounts, configurable by admins
- [alpha] Added DNS-01 upstream support for generic ACME finalizer
- [alpha] Added challenge_webhook configuration field to support finalization authorization setup
- Rewrote finalizers to use instanced configuration settings instead of global finalizer settings
- Added pre-authorizations. Administrators may add pre-authorized identifiers to accounts. Orders using these accounts will automatically be authorized for those identifiers at order creation.
- Allow deleting and viewing ACME finalizer bindings in the admin
- Changed the admin to redirect authentication to root instead of presenting bundled admin login
- Added more descriptive staged order status 
- [alpha] Added Huey task dashboard to admin
- [alpha] Added tasK_queue.stats_database configuration field to support custom Huey stats connection string

### Fixed

- Improved Helm chart startup and application health probes
- Fixed SAML backend administrators by group
- Improved generic finalizer error reporting
- Replaced some potential empty errors from finalizer upstreams with generic error messages
- Fixed pagination on account orders page not returning to correct tab

### Upgraded

- Upgraded all dependencies to latest minor release with uv sync --upgrade