This is a polymorphic property controlled by the `type` key. The following sections will show common configuration options as well as full documentation for every property.


### `certificat.finalizer.type: acme` {data-toc-label='acme' : #certificat.finalizer[acme]}
``` yaml
certificat:
  finalizer: 
    type: "acme"
    directory: "https://acme.com/directory"
    account_kid: "atTXZtcIpapuQnvikq...jkH1EagEJJoi7Ae"
    account_hmac_key: "Uaf92GO53kY8DJRw...eoYvyJLUUDoLiF"
    account_email: "contact@acme.edu"
```
#### `certificat.finalizer.account_email` {data-toc-label='account_email*' : #certificat.finalizer[acme].account_email}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Email address used as a contact when binding an account.

---

#### `certificat.finalizer.directory` {data-toc-label='directory*' : #certificat.finalizer[acme].directory}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Path to the ACME API endpoint. This usually ends with /directory.

---

#### `certificat.finalizer.account_hmac_key` {data-toc-label='account_hmac_key' : #certificat.finalizer[acme].account_hmac_key}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

External account binding HMAC key.

---

#### `certificat.finalizer.account_kid` {data-toc-label='account_kid' : #certificat.finalizer[acme].account_kid}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

External account binding key identifier.

---

#### `certificat.finalizer.finalization_timeout` {data-toc-label='finalization_timeout' : #certificat.finalizer[acme].finalization_timeout}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">90</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How long to poll the upstream server before finalization is canceled.

---

#### `certificat.finalizer.skip_answering_challenges` {data-toc-label='skip_answering_challenges' : #certificat.finalizer[acme].skip_answering_challenges}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Skip answering authorization challenges. This may be used if the upstream ACME server supports pre-authorization.

---

### `certificat.finalizer.type: certinext-acme` {data-toc-label='certinext-acme' : #certificat.finalizer[certinext-acme]}
``` yaml
certificat:
  finalizer: 
    type: "certinext-acme"
      # This binding should use a single-domain non-UCC profile
      single_domain_binding:
        directory: "https://acme-us.certinext.io/v1/directory"
        account_kid: "atTXZtcIpapuQnvikq...jkH1EagEJJoi7Ae"
        account_hmac_key: "Uaf92GO53kY8DJRw...eoYvyJLUUDoLiF"
        account_email: "contact@acme.edu"
      # This binding should use a UCC profile
      multi_domain_binding:
        directory: "https://acme-us.certinext.io/v1/directory"
        account_kid: "1emo4ehgTQyT9R...MPY6IjOL5EHm4PSmNL"
        account_hmac_key: "vYELs8X22sXymmQh6...e59l6IeAaSL0G4"
        account_email: "contact@acme.edu"
```
#### `certificat.finalizer.multi_domain_binding.account_email` {data-toc-label='multi_domain_binding.account_email*' : #certificat.finalizer[certinext-acme].multi_domain_binding.account_email}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Email address used when binding an account.

---

#### `certificat.finalizer.multi_domain_binding.directory` {data-toc-label='multi_domain_binding.directory*' : #certificat.finalizer[certinext-acme].multi_domain_binding.directory}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Path to the ACME API endpoint. This usually ends with /directory.

---

#### `certificat.finalizer.single_domain_binding.account_email` {data-toc-label='single_domain_binding.account_email*' : #certificat.finalizer[certinext-acme].single_domain_binding.account_email}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Email address used when binding an account.

---

#### `certificat.finalizer.single_domain_binding.directory` {data-toc-label='single_domain_binding.directory*' : #certificat.finalizer[certinext-acme].single_domain_binding.directory}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Path to the ACME API endpoint. This usually ends with /directory.

---

#### `certificat.finalizer.finalization_timeout` {data-toc-label='finalization_timeout' : #certificat.finalizer[certinext-acme].finalization_timeout}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">90</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How long to poll the upstream server before finalization is canceled.

---

#### `certificat.finalizer.multi_domain_binding.account_hmac_key` {data-toc-label='multi_domain_binding.account_hmac_key' : #certificat.finalizer[certinext-acme].multi_domain_binding.account_hmac_key}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

External account binding HMAC key.

---

#### `certificat.finalizer.multi_domain_binding.account_kid` {data-toc-label='multi_domain_binding.account_kid' : #certificat.finalizer[certinext-acme].multi_domain_binding.account_kid}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"External account binding key identifier."</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

---

#### `certificat.finalizer.single_domain_binding.account_hmac_key` {data-toc-label='single_domain_binding.account_hmac_key' : #certificat.finalizer[certinext-acme].single_domain_binding.account_hmac_key}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

External account binding HMAC key.

---

#### `certificat.finalizer.single_domain_binding.account_kid` {data-toc-label='single_domain_binding.account_kid' : #certificat.finalizer[certinext-acme].single_domain_binding.account_kid}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"External account binding key identifier."</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

---

#### `certificat.finalizer.skip_answering_challenges` {data-toc-label='skip_answering_challenges' : #certificat.finalizer[certinext-acme].skip_answering_challenges}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Skip answering authorization challenges. This may be used if the upstream ACME server supports pre-authorization.

---

### `certificat.finalizer.type: local` {data-toc-label='local' : #certificat.finalizer[local]}
``` yaml
certificat:
  finalizer: 
    type: local
    key: |
      -----BEGIN RSA PRIVATE KEY-----
      MIIEowIBAAKCAQEAld0nGypEoP0EKuY1K7PA7auFw94EZy0l2KkbkOcgsdykDcka
      ...GENERATE-YOUR-OWN...
      Wo7xleX2mpTnHQTjtv1NikkMkcIVMz0Y2pbLbhkYyQVG2v6lL4jB
      -----END RSA PRIVATE KEY-----
    cert: |
      -----BEGIN CERTIFICATE-----
      MIIC1DCCAbygAwIBAgIUQbnQ870aDubvty1Ph5DcCq92JnowDQYJKoZIhvcNAQEL
      ...GENERATE-YOUR-OWN...
      0aRuPpTug5Kgc1VrD97fjbNVn5Q/v0d8eL+eB7jujTSSXg/iBTH9D/0MSTp0u2Mm
      qIQFqQ2WEBc=
      -----END CERTIFICATE-----  
```
#### `certificat.finalizer.cert` {data-toc-label='cert*' : #certificat.finalizer[local].cert}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

PEM-formatted public key for the CA

---

#### `certificat.finalizer.key` {data-toc-label='key*' : #certificat.finalizer[local].key}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

PEM-formatted private key for the CA

---
