This is a polymorphic property controlled by the `type` key. The following sections will show common configuration options as well as full documentation for every property.


### `certificat.authentication.type: remote` {data-toc-label='remote' : #certificat.authentication[remote]}
``` yaml
certificat:
  authentication:
    type: remote
    administrators:
      - admin_username
    administrators_groups:
      - admin-group1
      - admin-group2
    user_header: HTTP_USER
    attribute_mapping:
      HTTP_MAIL: [email]
      HTTP_FIRSTNAME: [first_name]
      HTTP_LASTNAME: [last_name]
    redirect_template: https://auth.my.edu/authenticate?redirect={redirect}
```
#### `certificat.authentication.redirect_template` {data-toc-label='redirect_template*' : #certificat.authentication[remote].redirect_template}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>


Templated URL target for redirects. The redirect variable is substituted with the URL encoded path of the protected resource instead of the user returning to the root. This allows you to deep-link back to the protected resource.

For example, if a user attempted to access the protected resource `https://acme.edu/accounts/` and the authorization server lived at `https://auth.acme.edu/` 
you could set the redirect_template to `https://auth.acme.edu/?redirect_to={{ redirect }}`.

CertifiCat would redirect the request to `https://auth.acme.edu/?redirect_to=https%3A%2F%2Facme.edu%2Faccounts%2F`.


---

#### `certificat.authentication.administrators` {data-toc-label='administrators' : #certificat.authentication[remote].administrators}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of user principals who will automatically be given administrator privileges on login.

---

#### `certificat.authentication.administrators_groups` {data-toc-label='administrators_groups' : #certificat.authentication[remote].administrators_groups}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of groups that will automatically give included users administrator privileges on login.

---

#### `certificat.authentication.attribute_mapping` {data-toc-label='attribute_mapping' : #certificat.authentication[remote].attribute_mapping}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{
  "HTTP_USER_EMAIL": "email",
  "HTTP_USER_FIRSTNAME": "first_name",
  "HTTP_USER_LASTNAME": "last_name"
}
```

A dictionary mapping of src:targets where attributes are mapped from headers to Django attributes.

---

#### `certificat.authentication.force_logout_if_no_header` {data-toc-label='force_logout_if_no_header' : #certificat.authentication[remote].force_logout_if_no_header}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">true</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Destroys the user session if the remote header is not present. This should be turned off if the header is not transmitted with every request.

---

#### `certificat.authentication.groups_header` {data-toc-label='groups_header' : #certificat.authentication[remote].groups_header}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>

The header that will be used to populate groups. This is delimited by the groups_header_delimiter setting.
!!! example

    `HTTP_GROUPS`

---

#### `certificat.authentication.groups_header_delimiter` {data-toc-label='groups_header_delimiter' : #certificat.authentication[remote].groups_header_delimiter}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">";"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The delimiter used when parsing the groups_header value.

---

#### `certificat.authentication.log_http_headers` {data-toc-label='log_http_headers' : #certificat.authentication[remote].log_http_headers}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Adds header debugging to the web logs. Useful when debugging why user authentication is not behaving as expected.

---

#### `certificat.authentication.user_header` {data-toc-label='user_header' : #certificat.authentication[remote].user_header}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"HTTP_USER"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The header that will be used to populate user principal.

---

### `certificat.authentication.type: saml` {data-toc-label='saml' : #certificat.authentication[saml]}
``` yaml
certificat:
  authentication:
    type: saml
    administrators:
      - admin_username
    administrators_groups:
      - admin-group1
      - admin-group2
    attribute_mapping:
      mail: [username, email]
      uid: [username]
      eduPersonPrincipalName: [username]
      givenName: [first_name]
      sn: [last_name]
    sp:
      entity_id: "https://certificat.my.edu/saml2/metadata/"
      # key file mounted in the container
      key_file: "/etc/certificat/sp.key"
      # cert file mounted in the container
      cert_file: "/etc/certificat/sp.crt"
    idp:
      local: 
        # the location of the IdP metadata
        - "/etc/certificat/idp-metadata.xml"
```
#### `certificat.authentication.sp.cert_file` {data-toc-label='sp.cert_file*' : #certificat.authentication[saml].sp.cert_file}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The location of the PEM-formatted public key file.

---

#### `certificat.authentication.sp.entity_id` {data-toc-label='sp.entity_id*' : #certificat.authentication[saml].sp.entity_id}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

SAML service entity id. It should be unique and a URI.

---

#### `certificat.authentication.sp.key_file` {data-toc-label='sp.key_file*' : #certificat.authentication[saml].sp.key_file}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The location of the PEM-formatted private key file.

---

#### `certificat.authentication.administrators` {data-toc-label='administrators' : #certificat.authentication[saml].administrators}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of user principals who will automatically be given administrator privileges on login.

---

#### `certificat.authentication.administrators_groups` {data-toc-label='administrators_groups' : #certificat.authentication[saml].administrators_groups}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of groups that will automatically give administrator privileges to any included users on login.

---

#### `certificat.authentication.attribute_mapping` {data-toc-label='attribute_mapping' : #certificat.authentication[saml].attribute_mapping}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{
  "uid": [
    "username"
  ],
  "eduPersonPrincipalName": [
    "username"
  ],
  "eduPersonTargetedID": [
    "username"
  ],
  "mail": [
    "email"
  ],
  "givenName": [
    "first_name"
  ],
  "sn": [
    "last_name"
  ]
}
```


A dictionary mapping of src:[target] where attributes are mapped from SAML responses to Django attributes.

The default mapping is a best-effort guess at how attributes may flow from the IdP to the CertifiCat service. Depending on attribute naming
you may need to adjust these. For example, consider an IdP that sends the `urn:oid:0.9.2342.19200300.100.1.1` attribute for uid and the `urn:oid:0.9.2342.19200300.100.1.3` attribute for mail.

```yaml
certificat:
  authentication:
    attribute_mapping:
      "urn:oid:0.9.2342.19200300.100.1.1": ["username"]
      "urn:oid:0.9.2342.19200300.100.1.3": ["mail"]
      ...
```


---

#### `certificat.authentication.debug` {data-toc-label='debug' : #certificat.authentication[saml].debug}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

The debug setting for the Django SAML plugin. This increases log verbosity.

---

#### `certificat.authentication.group_attribute` {data-toc-label='group_attribute' : #certificat.authentication[saml].group_attribute}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"memberof"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The name (or translated name) of the group attribute in the returned SAML assertion

---

#### `certificat.authentication.group_sync_prefix` {data-toc-label='group_sync_prefix' : #certificat.authentication[saml].group_sync_prefix}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"SAML/"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

New groups synced from SAML will be prefixed with this identifier. Generally leave this setting as the default.

---

#### `certificat.authentication.idp.local` {data-toc-label='idp.local' : #certificat.authentication[saml].idp.local}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of local metadata files.

---

#### `certificat.authentication.idp.remote` {data-toc-label='idp.remote' : #certificat.authentication[saml].idp.remote}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;[RemoteIdP](#refs.RemoteIdP)&gt;</span></span>

A list of remote metadata providers.

---

#### `certificat.authentication.session_cookie` {data-toc-label='session_cookie' : #certificat.authentication[saml].session_cookie}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"snickerdoodle"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The name of the session cookie.

---

#### `certificat.authentication.sp.allow_unsolicited` {data-toc-label='sp.allow_unsolicited' : #certificat.authentication[saml].sp.allow_unsolicited}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">true</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Allow IdP-initiated SSO.

---

#### `certificat.authentication.sp.digest_algorithm` {data-toc-label='sp.digest_algorithm' : #certificat.authentication[saml].sp.digest_algorithm}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"http://www.w3.org/2001/04/xmlenc#sha256"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The default digest algorithm

---

#### `certificat.authentication.sp.force_authn` {data-toc-label='sp.force_authn' : #certificat.authentication[saml].sp.force_authn}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Disable SSO session reuse on login.

---

#### `certificat.authentication.sp.name` {data-toc-label='sp.name' : #certificat.authentication[saml].sp.name}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"CertifiCat"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The SP name in generated metadata.

---

#### `certificat.authentication.sp.signing_algorithm` {data-toc-label='sp.signing_algorithm' : #certificat.authentication[saml].sp.signing_algorithm}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The default signing algorithm.

---
