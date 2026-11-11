# External Account Binding

[External account binding (EAB)](https://datatracker.ietf.org/doc/html/rfc8555#section-7.3.4) is required for all CertifiCat ACME accounts. This associates a CertifiCat web account with an ACME account and allows ACME activity to be tracked through the web portal. It also prevents anonymous users from creating ACME accounts without first validating against your IdP.

Every user able to authenticate to CertifiCat is authorized to create a new external ACME account and then bind that account to a local ACME client.