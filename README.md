# RIT CertifiCat
### Overview

Rochester Institute of Technology’s CertifiCat is an ACME (Automated Certificate Management Environment) server that allows streamlined and efficient certificate management. RIT CertifiCat runs in your data center to make it easier to issue certificates to hosts with private IP addresses, restrictive inbound firewalls, or no internet access.

### Features
 - **ACME**: Tested with common ACME clients
   - Certbot
   - getssl
   - acme.sh
   - Posh-ACME
   - CNCF cert-manager
 - **Certificate Authorities**:
   - CERTINext Certificate Manager (ACME API)
   - Generic ACME Finalizer
   - Local Certificate Authority
 - **ACME Challenges**:
   - HTTP-01
   - DNS-01
 - **Authentication**:
   - SAML SSO with group access to ACME accounts
 - **Visualization**:
   - An attractive heat map
 - **Deployment methods**:
   - Docker
   - Kubernetes
   - Bare-metal
 - **Other features**:
   - RFC 1918 IP support
   - ACME toolkit to make EAB binding and key conversion easier
   - [certificat-ps PowerShell module](https://github.com/RIT-ITS/CertifiCat-PS) to make automating Posh-ACME easier

### Documentation
[View the official documentation](https://rit-its.github.io/CertifiCat/) for detailed examples and feature breakdowns.

### Getting Help
Use the GitHub issues feature if you encounter a bug or have questions. We’ll do our best to provide answers.

### Supporting the Project
GitHub pull requests are welcomed. If you have an idea, submit it as an issue, and we’ll look it over. If you want to help with more than bug fixes or ideas, contact the project owners at its-acme@rit.edu.

