# Finalizers

A finalizer submits a client's certificate signing request (CSR) to a certificate authority and stores the issued certificate. Every order passes through exactly one finalizer.

## Available finalizers

| Type | Purpose | Production use |
|---|---|---|
| [`local`](local.md) | Signs certificates with a CA key pair from the configuration file. | No. Evaluation only. |
| [`acme`](acme.md) | Forwards orders to any upstream ACME server. | Yes |
| [`certinext-acme`](certinext-acme.md) | Forwards orders to CERTInext through two ACME integrations. | Yes |

The finalizer is set in [certificat.finalizer](../configuration/index.md#certificat.finalizer.section). The `type` key selects the finalizer and determines which other keys are valid.

## Where finalization fits in an order

1. The ACME client creates an order, and CertifiCat validates the client's challenges, or applies [pre-authorizations](../features/index.md#pre-authorizations).
2. The order becomes `ready`, and the client submits its CSR.
3. The order becomes `processing`, and CertifiCat queues a finalization task.
4. The task worker runs the account's finalizer.
5. On success the certificate is stored and the order becomes `valid`. The client downloads the certificate on its next poll.

Finalization runs in the task worker, not the web server. Orders stay in `processing` if the task worker is not running.

## Finalizer selection

Each order is finalized by the finalizer of the account that created it:

- By default, accounts use the finalizer in `certificat.finalizer`.
- Anyone who can edit an account can assign it one of the [alternative finalizers](multiple.md).
- If the assigned alternative finalizer no longer exists in the configuration, the default finalizer is used.

## Retries and failures

When finalization fails, the outcome depends on the type of failure.

| Failure | Result |
|---|---|
| The upstream certificate authority returns an error, times out, or rejects account registration. | The order becomes `invalid` immediately. It is not retried. |
| Any other unexpected error. | The task is retried. |

Retries are controlled by two settings:

| Setting | Default | Description |
|---|---|---|
| [finalize_max_retries](../configuration/index.md#certificat.finalize_max_retries) | `10` | Retries before the order is marked `invalid`. |
| [finalize_retry_delay](../configuration/index.md#certificat.finalize_retry_delay) | `10` | Seconds between retries. |

Every error is recorded on the order. Users see it on the order page, both as a finalization error and as an event in the order's history. ACME clients receive the order as `invalid`. To finalize again, the client must create a new order.

## Troubleshooting

- **Error details.** Check the order page first. Finalizers report upstream ACME errors in the form `<type>: <description> :: <detail>`.
- **Logs.** Finalizer activity is logged by the task worker, not the web server. Set [certificat.logging](../configuration/index.md#certificat.logging.section) to `DEBUG` for more detail.
- **Stuck orders.** The **Health** section of `/admin/` warns when orders have been `processing` for more than an hour.
