# Finalizers

<!-- md:config `certificat.finalizer.section` `certificat.finalizer` -->

A finalizer submits the client's CSR to a certificate authority and returns the issued certificate. CertifiCat uses one default finalizer, and anyone who can edit an account can assign it an alternative finalizer.

| Finalizer | Use |
|---|---|
| [Local](../finalizers/local.md) | Evaluation only. Signs certificates with a CA key pair from the configuration file. |
| [ACME](../finalizers/acme.md) | Any upstream certificate authority with an ACME API. |
| [CERTInext ACME](../finalizers/certinext-acme.md) | CERTInext, with separate single-domain and multi-domain integrations. |