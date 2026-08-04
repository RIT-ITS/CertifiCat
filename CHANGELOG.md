# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses modified [Calendar Versioning](https://calver.org/).

## [2026.8.2] - 2024-08-01

### Fixed

- Fixed ssl database option lookup for Huey stats connection

## [2026.8.1] - 2024-08-01

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