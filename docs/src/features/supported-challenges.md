# ACME Challenges

<!-- md:config `acme.challenges_available` -->

All ACME clients are required to answer challenges by default. 

CertifiCat supports a few different [identifier validation challenges](https://datatracker.ietf.org/doc/html/rfc8555#section-8) and strategies.

## HTTP-01

<!-- md:badge `:material-cog-outline:` `"http-01"` -->

This is the preferred challenge method. It requires the CertifiCat server to have "line-of-sight" to the requesting server and also requires port 80 to be open. [In response to overeager systems admins, LetsEncrypt has drafted a best practice on keeping port 80 open.](https://letsencrypt.org/docs/allow-port-80/)

This method is simple and easy to automate consistently.

---

## DNS-01

<!-- md:badge `:material-cog-outline:` `"dns-01"` -->

For some institutions or applications HTTP-01 can be impractical. CertifiCat also supports `DNS-01` challenges. This is more difficult to implement for a few different reasons. 

- The operator must be given correctly-scoped access to modify DNS; an external service
- The operator must build in time and checks to verify DNS has propagated before signaling to CertifiCat to continue

---

## Pre-Authorizations

Administrators may also configure pre-authorized identifiers per account using the account management web interface. Any orders from the configured account with identifiers matching the pre-configured ones will automatically create valid authorizations. This is usually used sparingly with services that have significant roadblocks to `DNS-01` or `HTTP-01` challenges.
