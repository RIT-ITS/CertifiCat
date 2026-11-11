# Features

An ACME order transaction consists of three parties.

- **ACME client**: Creates the CSR and may control reloading services when the certificate is downloaded.
- **CertifiCat**: Answers requests from the ACME client and proxies the CSR to an upstream authority.
- **Certificate Authority**: The service ultimately responsible for processing the CSR and creating a certificate.

The following diagram illustrates the ideal path for an ACME transaction including new account creation. CertifiCat ACME features are grouped and documented by how they extend and support the ACME protocol.

```mermaid
sequenceDiagram
    participant user@{ "type": "actor" } as User
    participant client as ACME Client
    participant certificat@{ "type": "boundary" } as CertifiCat ACME Proxy
    participant authority@{ "type": "control" } as Certificate Authority

    autonumber
    user->>certificat: Authenticate
    user->>certificat: Create New CertifiCat Account

    client->>certificat: Register New ACME Account with Binding
    client->>certificat: Create New Order
    
    Note over certificat: Order: pending

    client->>certificat: Request Authorizations
    loop 
        client->>client: Prepare Challenges<br/>
    end
    client->>certificat: Indicate Challenges Prepared
    loop
        certificat->>client: Validate Challenges
    end

    Note over certificat: Order: ready

    client->>certificat: Submit CSR

    Note over certificat: Order: processing

    loop
        client->>certificat: Poll Order Status
    end

    Note over certificat: Finalizer Selection
    certificat->>authority: Submit Order
    authority->>certificat: Return Certificate
    
    Note over certificat: Order: valid

    client->>certificat: Download Certificate

```