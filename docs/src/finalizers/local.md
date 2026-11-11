# Local Finalizer

<!-- md:config `certificat.finalizer[local]` -->

The `local` finalizer signs certificates with a CA key pair that you provide in the configuration file. It does not contact an external certificate authority.

!!! warning
    The local finalizer is for evaluation and testing only. The CA private key is stored in the configuration file, and issued certificates are not trusted by any client. Switch away from this finalizer as soon as initial setup is complete.

## Issued certificates

| Property | Value |
|---|---|
| Subject | Copied from the CSR. |
| Extensions | Copied from the CSR, including subject alternative names. |
| Issuer | The CA certificate's subject. |
| Validity | 90 days from issuance. |
| Signature | SHA-256 with the CA key. |
| Chain returned to the client | The issued certificate followed by the CA certificate. |

## Configuration

### 1. Create a test CA

``` bash
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -subj "/CN=CertifiCat Test CA" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign" \
  -keyout ca.key -out ca.crt
```

The key must not be encrypted.

### 2. Add the key pair to the configuration

The `key` and `cert` options contain the PEM text itself, not file paths. Use YAML block scalars (`|`) to keep the line breaks:

``` yaml
certificat:
  finalizer:
    type: "local"
    key: |
      -----BEGIN PRIVATE KEY-----
      MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
      -----END PRIVATE KEY-----
    cert: |
      -----BEGIN CERTIFICATE-----
      MIIDGzCCAgOgAwIBAgIURi50F+f9rZj/93Q/GPxnqovz2wEw...
      -----END CERTIFICATE-----
```

| Option | Required | Description |
|---|---|---|
| `key` | Yes | PEM-formatted, unencrypted CA private key. |
| `cert` | Yes | PEM-formatted CA certificate. |
