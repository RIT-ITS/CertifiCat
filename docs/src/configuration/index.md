# Configuration Reference

CertifiCat is configured through a strongly-typed YAML configuration file powered by [Pydantic](https://pydantic.dev/). An environment variable named `CERTIFICAT__CONFIG` must contain the absolute path to this file at startup.

Configuration options are frequently referenced in dot notation. When you see `certificat.redis.host` that expands to the following:

``` yaml
certificat:
  redis:
    host: "redis.acme.edu"
```
## acme {data-toc-label="acme"}

These settings are provided to the [acmev2](https://github.com/RIT-ITS/acmev2) module.

-8<- "configuration/acme.toplevel.md"

## certificat {data-toc-label="certificat"}

-8<- "configuration/certificat.toplevel.md"

## certificat.authentication {: #certificat.authentication.section}

-8<- "configuration/certificat.authentication.md"

## certificat.db {: #certificat.db.section}

-8<- "configuration/certificat.db.md"

## certificat.finalizer {: #certificat.finalizer.section}

-8<- "configuration/certificat.finalizer.md"

## certificat.redis {: #certificat.redis.section}

!!! example

    ``` yaml
    certificat:
      redis:
        host: "redis.acme.edu"
        password: "s3cuR3-p@ssw0rd"
    ```

-8<- "configuration/certificat.redis.md"

## certificat.logging {: #certificat.logging.section}

!!! example

    ``` yaml
    certificat:
      logging:
        django_level: "DEBUG"
    ```

-8<- "configuration/certificat.logging.md"

## certificat.theming {: #certificat.theming.section}

-8<- "configuration/certificat.theming.md"

## Full Reference

-8<- "configuration/references.md"