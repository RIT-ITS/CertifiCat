# Notifications

<!-- md:config `certificat.notifications` -->

CertifiCat can send notifications about various events through [Apprise](https://github.com/caronc/apprise), which supports email, Slack, Microsoft Teams, webhooks, and many other services.

!!! note "Beta"
    Notifications are in beta. Message content may change.

## Events

| Event | Sent when | Message |
|---|---|---|
| <!-- md:nowrap_key `on_finalization_success` --> | A finalizer returns a certificate. | `Order <order> finalized successfully` |
| <!-- md:nowrap_key `on_finalization_error` --> | Finalization fails and the order is marked `invalid`. | `Order <order> had an error during finalization` |

## Configuration

Each event takes a list of [Apprise URLs](https://github.com/caronc/apprise/wiki#notification-services):

``` yaml
certificat:
  notifications:
    on_finalization_success:
      services:
        - "mailtos://user:password@smtp.acme.edu?to=pki-team@acme.edu"
    on_finalization_error:
      enabled: true
      services:
        - "mailtos://user:password@smtp.acme.edu?to=pki-team@acme.edu"
        - "msteams://<token_a>/<token_b>/<token_c>/"
```

| Option | Default | Description |
|---|---|---|
| `enabled` | `true` | Send notifications for this event. |
| `services` | `[]` | Apprise URLs to notify. |

## Testing a service URL

CertifiCat has included a custom `stdout://` notification handler. Configure this logger as a service URI to test logging.

``` yaml
certificat:
  notifications:
    on_finalization_success:
      services:
        - "stdout://"
```
