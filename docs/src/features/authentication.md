# Authentication

<!-- md:config `certificat.authentication.section` `certificat.authentication` -->

CertifiCat requires authentication, it does not operate as an anonymous ACME proxy. 

## SAML

<!-- md:config `certificat.authentication[saml]` -->

SAML is the preferred and best-supported authentication method. When configuring SAML you need the following data:

- <!-- md:config `certificat.url_root` -->
- PEM-formatted public/private key pair
- IdP XML Metadata
- SAML Attribute Statement

### Configuration

1. Set <!-- md:config `certificat.authentication[saml].sp.entity_id` `certificat.authentication.sp.entity_id` --> to your chosen entity ID. A good rule of thumb is to use the domain for CertifiCat and append a path. For example: `https://acme.edu/saml2`.

2. Generate the PEM-formatted key 
    - Set <!-- md:config `certificat.authentication[saml].sp.key_file` `certificat.authentication.sp.key_file` --> to the private key location
    - Set <!-- md:config `certificat.authentication[saml].sp.cert_file` `certificat.authentication.sp.cert_file` --> to the public key location

3. Download the IdP metadata
    - Set <!-- md:config `certificat.authentication[saml].idp.local` `certificat.authentication.idp.local` -->array to the metadata location 

    ``` yaml title="minimal example"
    certificat:
      authentication:
        type: saml
        sp:
          entity_id: "https://acme.edu/saml2"
          key_file: "/etc/certificat/sp.key"
          cert_file: "/etc/certificat/sp.crt"
        idp:
          local:
            - "/etc/certificat/idp-metadata.xml"
    ```

4. Configure attribute mapping. [Read the documentation for examples](../configuration/index.md#certificat.authentication[saml].attribute_mapping) of how to map your attributes if mapping is not working.

### Troubleshooting

Set <!-- md:config `certificat.authentication[saml].debug` `certificat.authentication.debug` --> to `True` to enable debug logs and consult the web logs when a user is attempting to authenticate.

---

## Remote

<!-- md:config `certificat.authentication[remote]` -->

!!! warning

    When using the remote authentication method, it's critical that no clients can connect directly to CertifiCat or directly set the `user_header`. CertifiCat relies on network security and upstream header stripping to ensure the headers it receives are valid.

### Configuration 

Remote authentication uses headers from a trusted proxy to automatically authenticate a user. Visit the configuration reference for a detailed example of how to configure authentication.

### Troubleshooting

Set <!-- md:config `certificat.authentication[remote].log_http_headers` `certificat.authentication.log_http_headers` --> to `True` to enable debug logs and consult the web logs when a user is attempting to authenticate.