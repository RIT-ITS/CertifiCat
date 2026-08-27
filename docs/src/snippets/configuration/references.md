### ACMEFinalizerSettings {: #refs.ACMEFinalizerSettings}
#### `ACMEFinalizerSettings.account_email` {data-toc-label='account_email*' : #ACMEFinalizerSettings.account_email}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Email address used as a contact when binding an account.

---

#### `ACMEFinalizerSettings.directory` {data-toc-label='directory*' : #ACMEFinalizerSettings.directory}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Path to the ACME API endpoint. This usually ends with /directory.

---

#### `ACMEFinalizerSettings.account_hmac_key` {data-toc-label='account_hmac_key' : #ACMEFinalizerSettings.account_hmac_key}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

External account binding HMAC key.

---

#### `ACMEFinalizerSettings.account_kid` {data-toc-label='account_kid' : #ACMEFinalizerSettings.account_kid}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

External account binding key identifier.

---

#### `ACMEFinalizerSettings.finalization_timeout` {data-toc-label='finalization_timeout' : #ACMEFinalizerSettings.finalization_timeout}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">90</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How long to poll the upstream server before finalization is canceled.

---

#### `ACMEFinalizerSettings.skip_answering_challenges` {data-toc-label='skip_answering_challenges' : #ACMEFinalizerSettings.skip_answering_challenges}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Skip answering authorization challenges. This may be used if the upstream ACME server supports pre-authorization.

---

### AlternativeFinalizerSettings {: #refs.AlternativeFinalizerSettings}
#### `AlternativeFinalizerSettings.description` {data-toc-label='description*' : #AlternativeFinalizerSettings.description}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

A short description of the finalizer. This is presented in user interfaces when making selections.

---

#### `AlternativeFinalizerSettings.finalizer` {data-toc-label='finalizer*' : #AlternativeFinalizerSettings.finalizer}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">polymorphic</span></span>

Which order finalizer module to use.
!!! example

    `local` `acme` `certinext-acme`

This is a polymorphic property controlled by the `AlternativeFinalizerSettings.finalizer.type` key, which means the shape of the configuration is different depending on the implementation. This property can be configured using the following types:


 - [acme](#AlternativeFinalizerSettings.finalizer.type[acme])
 - [certinext-acme](#AlternativeFinalizerSettings.finalizer.type[certinext-acme])
 - [local](#AlternativeFinalizerSettings.finalizer.type[local])

---

#### `AlternativeFinalizerSettings.id` {data-toc-label='id*' : #AlternativeFinalizerSettings.id}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Unique ID for this finalizer. This will be stored in the account and used to select the correct finalizer at certificate creation.

---

#### `AlternativeFinalizerSettings.name` {data-toc-label='name*' : #AlternativeFinalizerSettings.name}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

A short descriptive name for the finalizer. This is presented in user interfaces when making selections.

---

### ApplicationSettings {: #refs.ApplicationSettings}
#### `ApplicationSettings.authentication` {data-toc-label='authentication*' : #ApplicationSettings.authentication}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">polymorphic</span></span>

Authentication settings for the web frontend. This controls how you authenticate and automatically provision access to the CertifiCat HTML service.

This is a polymorphic property controlled by the `ApplicationSettings.authentication.type` key, which means the shape of the configuration is different depending on the implementation. This property can be configured using the following types:


 - [remote](#ApplicationSettings.authentication.type[remote])
 - [saml](#ApplicationSettings.authentication.type[saml])

---

#### `ApplicationSettings.db` {data-toc-label='db*' : #ApplicationSettings.db}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">polymorphic</span></span>

Database connection settings. CertifiCat requires an external database to store ACME and management state.

This is a polymorphic property controlled by the `ApplicationSettings.db.type` key, which means the shape of the configuration is different depending on the implementation. This property can be configured using the following types:


 - [mysql](#ApplicationSettings.db.type[mysql])
 - [postgresql](#ApplicationSettings.db.type[postgresql])

---

#### `ApplicationSettings.finalizer` {data-toc-label='finalizer*' : #ApplicationSettings.finalizer}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">polymorphic</span></span>

Which order finalizer module to use. The server is designed to finalize all requests against one default backend. This will be the backend initially used by all accounts.

This is a polymorphic property controlled by the `ApplicationSettings.finalizer.type` key, which means the shape of the configuration is different depending on the implementation. This property can be configured using the following types:


 - [acme](#ApplicationSettings.finalizer.type[acme])
 - [certinext-acme](#ApplicationSettings.finalizer.type[certinext-acme])
 - [local](#ApplicationSettings.finalizer.type[local])

---

#### `ApplicationSettings.redis` {data-toc-label='redis*' : #ApplicationSettings.redis}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>

Redis connection settings. CertifiCat requires Redis to store cache and faciliate background jobs.

[:material-shape: View Type Reference](#refs.RedisSettings)

---

#### `ApplicationSettings.secret_key` {data-toc-label='secret_key*' : #ApplicationSettings.secret_key}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>


[Django SECRET_KEY.](https://docs.djangoproject.com/en/6.1/ref/settings/#std-setting-SECRET_KEY) This should be set to a unique, unpredictable value.

You can generate a secret key by using the following snippet: 

``` bash
tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50; echo
```


---

#### `ApplicationSettings.url_root` {data-toc-label='url_root*' : #ApplicationSettings.url_root}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>


The url root is used to generate absolute urls to the application. It should not contain path and parameters.
!!! warning
    If your url_root changes your existing ACME accounts will become unusable. This is due to [request URL integrity](https://datatracker.ietf.org/doc/html/rfc8555#section-6.4).

!!! example

    `https://acme.edu/`

---

#### `ApplicationSettings.alternative_finalizers` {data-toc-label='alternative_finalizers' : #ApplicationSettings.alternative_finalizers}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;[AlternativeFinalizerSettings](#refs.AlternativeFinalizerSettings)&gt;</span></span>

A list of alternative finalizers that can be used to request certificates through manual configuration.
!!! example

    
    ``` yaml
    certificat: 
      alternative_finalizers:
        - id: "alt-finalizer-1"
          name: "Alternative Finalizer 1"
          description: "A description for the web UI"
          finalizer: ... certificat.finalizer ...
    
        - id: "alt-finalizer-2"
          name: "Alternative Finalizer 2"
          description: "A different description for the web UI"
          finalizer: ... certificat.finalizer ...
    ```

---

#### `ApplicationSettings.beacon_enabled` {data-toc-label='beacon_enabled' : #ApplicationSettings.beacon_enabled}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">true</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Send tracking information about platform usage to RIT.

---

#### `ApplicationSettings.challenge_max_retries` {data-toc-label='challenge_max_retries' : #ApplicationSettings.challenge_max_retries}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">5</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How many challenge retries to perform before marking the challenge invalid.

---

#### `ApplicationSettings.challenge_retry_delay` {data-toc-label='challenge_retry_delay' : #ApplicationSettings.challenge_retry_delay}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">2</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How long to wait between challenge retries in seconds.

---

#### `ApplicationSettings.delete_invalid_orders` {data-toc-label='delete_invalid_orders' : #ApplicationSettings.delete_invalid_orders}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">true</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Purge invalid orders after some amount of time.

---

#### `ApplicationSettings.finalize_max_retries` {data-toc-label='finalize_max_retries' : #ApplicationSettings.finalize_max_retries}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">10</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How many order finalization retries to perform before marking the order invalid.

---

#### `ApplicationSettings.finalize_retry_delay` {data-toc-label='finalize_retry_delay' : #ApplicationSettings.finalize_retry_delay}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">10</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How long to wait between order finalization retries in seconds.

---

#### `ApplicationSettings.healthcheck_allowed_networks` {data-toc-label='healthcheck_allowed_networks' : #ApplicationSettings.healthcheck_allowed_networks}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">["127.0.0.1/32"]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

Networks allowed to access the health endpoints.

---

#### `ApplicationSettings.hmac_id_length` {data-toc-label='hmac_id_length' : #ApplicationSettings.hmac_id_length}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">40</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

The length of the hmac id generated for an ACME external account binding.

---

#### `ApplicationSettings.hmac_key_length` {data-toc-label='hmac_key_length' : #ApplicationSettings.hmac_key_length}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">90</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

The length of the hmac key generated for an ACME external account binding.

---

#### `ApplicationSettings.logging` {data-toc-label='logging' : #ApplicationSettings.logging}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{
  "certificat_level": "INFO",
  "huey_level": "INFO",
  "django_level": "INFO",
  "acmev2_level": "INFO",
  "root_level": "INFO"
}
```

Logging levels for CertifiCat components

[:material-shape: View Type Reference](#refs.LoggingSettings)

---

#### `ApplicationSettings.session_cookie_age` {data-toc-label='session_cookie_age' : #ApplicationSettings.session_cookie_age}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">28800</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

Django SESSION_COOKIE_AGE. This is the maximum age of the session cookie in seconds.

---

#### `ApplicationSettings.show_version` {data-toc-label='show_version' : #ApplicationSettings.show_version}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Show the version on the website.

---

#### `ApplicationSettings.task_queue` {data-toc-label='task_queue' : #ApplicationSettings.task_queue}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{
  "workers": 20,
  "stats_database": null
}
```

Settings for the Redis-powered Huey task queue.

[:material-shape: View Type Reference](#refs.TaskQueueSettings)

---

#### `ApplicationSettings.theming` {data-toc-label='theming' : #ApplicationSettings.theming}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{
  "global_css": null
}
```

Theming and customization settings for the web front-end.

[:material-shape: View Type Reference](#refs.ThemeSettings)

---

#### `ApplicationSettings.time_zone` {data-toc-label='time_zone' : #ApplicationSettings.time_zone}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"America/New_York"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Django TIME_ZONE, used mostly for date localization.

---

### CERTINextACMEFinalizerSettings {: #refs.CERTINextACMEFinalizerSettings}
#### `CERTINextACMEFinalizerSettings.multi_domain_binding` {data-toc-label='multi_domain_binding*' : #CERTINextACMEFinalizerSettings.multi_domain_binding}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>

ACME credentials used when creating a multi-domain certificate.

[:material-shape: View Type Reference](#refs.CERTINextExternalAccountBinding)

---

#### `CERTINextACMEFinalizerSettings.single_domain_binding` {data-toc-label='single_domain_binding*' : #CERTINextACMEFinalizerSettings.single_domain_binding}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>

ACME credentials used when creating a single-domain certificate.

[:material-shape: View Type Reference](#refs.CERTINextExternalAccountBinding)

---

#### `CERTINextACMEFinalizerSettings.finalization_timeout` {data-toc-label='finalization_timeout' : #CERTINextACMEFinalizerSettings.finalization_timeout}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">90</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How long to poll the upstream server before finalization is canceled.

---

#### `CERTINextACMEFinalizerSettings.skip_answering_challenges` {data-toc-label='skip_answering_challenges' : #CERTINextACMEFinalizerSettings.skip_answering_challenges}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Skip answering authorization challenges. This may be used if the upstream ACME server supports pre-authorization.

---

### CERTINextExternalAccountBinding {: #refs.CERTINextExternalAccountBinding}
#### `CERTINextExternalAccountBinding.account_email` {data-toc-label='account_email*' : #CERTINextExternalAccountBinding.account_email}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Email address used when binding an account.

---

#### `CERTINextExternalAccountBinding.directory` {data-toc-label='directory*' : #CERTINextExternalAccountBinding.directory}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Path to the ACME API endpoint. This usually ends with /directory.

---

#### `CERTINextExternalAccountBinding.account_hmac_key` {data-toc-label='account_hmac_key' : #CERTINextExternalAccountBinding.account_hmac_key}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

External account binding HMAC key.

---

#### `CERTINextExternalAccountBinding.account_kid` {data-toc-label='account_kid' : #CERTINextExternalAccountBinding.account_kid}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"External account binding key identifier."</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

---

### Challenges {: #refs.Challenges}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">enum</span></span>

 - `"custom"`
 - `"dns-01"`
 - `"http-01"`


---

### LocalACMESettings {: #refs.LocalACMESettings}
#### `LocalACMESettings.authorization_client_delay` {data-toc-label='authorization_client_delay' : #LocalACMESettings.authorization_client_delay}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">15</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

The Retry-After header sent to ACME clients.

---

#### `LocalACMESettings.blacklisted_domains` {data-toc-label='blacklisted_domains' : #LocalACMESettings.blacklisted_domains}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

The server will refuse to issue domains for any identifiers in this list. It supports regular expressions.

---

#### `LocalACMESettings.challenges_available` {data-toc-label='challenges_available' : #LocalACMESettings.challenges_available}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">["http-01"]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;[Challenges](#refs.Challenges)&gt;</span></span>

Default set of challenges created when an authorization is created

---

#### `LocalACMESettings.dns_challenge_nameservers` {data-toc-label='dns_challenge_nameservers' : #LocalACMESettings.dns_challenge_nameservers}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of servers in the format ip or ip:port. The DNS challenge resolver will use these nameservers. If left blank the system nameservers will be used.

---

#### `LocalACMESettings.eab_required` {data-toc-label='eab_required' : #LocalACMESettings.eab_required}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Whether all accounts are required to use external account binding or not.

---

#### `LocalACMESettings.http_01_challenge_user_agent` {data-toc-label='http_01_challenge_user_agent' : #LocalACMESettings.http_01_challenge_user_agent}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"python-acmev2/0.2.1"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

User agent the http-01 challenge validator uses when requesting the challenge document from the client server

---

#### `LocalACMESettings.mask_order_processing_status_ua_match` {data-toc-label='mask_order_processing_status_ua_match' : #LocalACMESettings.mask_order_processing_status_ua_match}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"^cert-manager-clusterissuers.*"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Any order requests from this user agent will mask the processing state as pending

---

#### `LocalACMESettings.max_identifiers` {data-toc-label='max_identifiers' : #LocalACMESettings.max_identifiers}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">50</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

Max number of identifiers that can be passed to a new order request.

---

#### `LocalACMESettings.resource_expiration_delta` {data-toc-label='resource_expiration_delta' : #LocalACMESettings.resource_expiration_delta}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"PT8H"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

How long should the order and authorization objects be valid for after generation?

---

### LocalFinalizerSettings {: #refs.LocalFinalizerSettings}
#### `LocalFinalizerSettings.cert` {data-toc-label='cert*' : #LocalFinalizerSettings.cert}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

PEM-formatted public key for the CA

---

#### `LocalFinalizerSettings.key` {data-toc-label='key*' : #LocalFinalizerSettings.key}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

PEM-formatted private key for the CA

---

### LoggingSettings {: #refs.LoggingSettings}
#### `LoggingSettings.acmev2_level` {data-toc-label='acmev2_level' : #LoggingSettings.acmev2_level}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"INFO"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>

Logging level for ACME server component.

---

#### `LoggingSettings.certificat_level` {data-toc-label='certificat_level' : #LoggingSettings.certificat_level}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"INFO"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>

Logging level for the CertifiCat frontend.

---

#### `LoggingSettings.django_level` {data-toc-label='django_level' : #LoggingSettings.django_level}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"INFO"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>

Logging level for Django components.

---

#### `LoggingSettings.huey_level` {data-toc-label='huey_level' : #LoggingSettings.huey_level}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"INFO"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>

Logging level for the task runner.

---

#### `LoggingSettings.root_level` {data-toc-label='root_level' : #LoggingSettings.root_level}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"INFO"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>

Logging level for root logger.

---

### MariaDBDatabaseSettings {: #refs.MariaDBDatabaseSettings}
#### `MariaDBDatabaseSettings.name` {data-toc-label='name*' : #MariaDBDatabaseSettings.name}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The database to use after a connection is established.

---

#### `MariaDBDatabaseSettings.user` {data-toc-label='user*' : #MariaDBDatabaseSettings.user}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

User for the database connection.

---

#### `MariaDBDatabaseSettings.host` {data-toc-label='host' : #MariaDBDatabaseSettings.host}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Host for the database connection.

---

#### `MariaDBDatabaseSettings.options` {data-toc-label='options' : #MariaDBDatabaseSettings.options}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{}
```

Key-value options passed to the driver.

---

#### `MariaDBDatabaseSettings.password` {data-toc-label='password' : #MariaDBDatabaseSettings.password}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Password for the database connection.

---

#### `MariaDBDatabaseSettings.port` {data-toc-label='port' : #MariaDBDatabaseSettings.port}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">3306</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

Port for the database connection.

---

### PostgresDatabaseSettings {: #refs.PostgresDatabaseSettings}
#### `PostgresDatabaseSettings.name` {data-toc-label='name*' : #PostgresDatabaseSettings.name}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The database to use after a connection is established.

---

#### `PostgresDatabaseSettings.user` {data-toc-label='user*' : #PostgresDatabaseSettings.user}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

User for the database connection.

---

#### `PostgresDatabaseSettings.host` {data-toc-label='host' : #PostgresDatabaseSettings.host}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Host for the database connection.

---

#### `PostgresDatabaseSettings.options` {data-toc-label='options' : #PostgresDatabaseSettings.options}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{}
```

Key-value options passed to the driver.

---

#### `PostgresDatabaseSettings.password` {data-toc-label='password' : #PostgresDatabaseSettings.password}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Password for the database connection.

---

#### `PostgresDatabaseSettings.port` {data-toc-label='port' : #PostgresDatabaseSettings.port}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">5432</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

Port for the database connection.

---

### RedisSettings {: #refs.RedisSettings}
#### `RedisSettings.host` {data-toc-label='host*' : #RedisSettings.host}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Host for the Redis connection.

---

#### `RedisSettings.password` {data-toc-label='password*' : #RedisSettings.password}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Password for the Redis connection.

---

#### `RedisSettings.port` {data-toc-label='port' : #RedisSettings.port}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">6379</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

Port for the Redis connection.

---

### RemoteAuthSettings {: #refs.RemoteAuthSettings}
#### `RemoteAuthSettings.redirect_template` {data-toc-label='redirect_template*' : #RemoteAuthSettings.redirect_template}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>


Templated URL target for redirects. The redirect variable is substituted with the URL encoded path of the protected resource instead of the user returning to the root. This allows you to deep-link back to the protected resource.

For example, if a user attempted to access the protected resource `https://acme.edu/accounts/` and the authorization server lived at `https://auth.acme.edu/` 
you could set the redirect_template to `https://auth.acme.edu/?redirect_to={{ redirect }}`.

CertifiCat would redirect the request to `https://auth.acme.edu/?redirect_to=https%3A%2F%2Facme.edu%2Faccounts%2F`.


---

#### `RemoteAuthSettings.administrators` {data-toc-label='administrators' : #RemoteAuthSettings.administrators}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of user principals who will automatically be given administrator privileges on login.

---

#### `RemoteAuthSettings.administrators_groups` {data-toc-label='administrators_groups' : #RemoteAuthSettings.administrators_groups}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of groups that will automatically give included users administrator privileges on login.

---

#### `RemoteAuthSettings.attribute_mapping` {data-toc-label='attribute_mapping' : #RemoteAuthSettings.attribute_mapping}
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

#### `RemoteAuthSettings.force_logout_if_no_header` {data-toc-label='force_logout_if_no_header' : #RemoteAuthSettings.force_logout_if_no_header}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">true</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Destroys the user session if the remote header is not present. This should be turned off if the header is not transmitted with every request.

---

#### `RemoteAuthSettings.groups_header` {data-toc-label='groups_header' : #RemoteAuthSettings.groups_header}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>

The header that will be used to populate groups. This is delimited by the groups_header_delimiter setting.
!!! example

    `HTTP_GROUPS`

---

#### `RemoteAuthSettings.groups_header_delimiter` {data-toc-label='groups_header_delimiter' : #RemoteAuthSettings.groups_header_delimiter}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">";"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The delimiter used when parsing the groups_header value.

---

#### `RemoteAuthSettings.log_http_headers` {data-toc-label='log_http_headers' : #RemoteAuthSettings.log_http_headers}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Adds header debugging to the web logs. Useful when debugging why user authentication is not behaving as expected.

---

#### `RemoteAuthSettings.user_header` {data-toc-label='user_header' : #RemoteAuthSettings.user_header}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"HTTP_USER"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The header that will be used to populate user principal.

---

### RemoteIdP {: #refs.RemoteIdP}
#### `RemoteIdP.url` {data-toc-label='url*' : #RemoteIdP.url}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

IdP metadata URL.

---

#### `RemoteIdP.cert` {data-toc-label='cert' : #RemoteIdP.cert}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>

Signing certificate for the remote metadata.

---

### SAMLAuthSettings {: #refs.SAMLAuthSettings}
#### `SAMLAuthSettings.idp` {data-toc-label='idp*' : #SAMLAuthSettings.idp}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>

[:material-shape: View Type Reference](#refs.SAMLIdPSettings)

---

#### `SAMLAuthSettings.sp` {data-toc-label='sp*' : #SAMLAuthSettings.sp}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>

[:material-shape: View Type Reference](#refs.SAMLSPSettings)

---

#### `SAMLAuthSettings.administrators` {data-toc-label='administrators' : #SAMLAuthSettings.administrators}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of user principals who will automatically be given administrator privileges on login.

---

#### `SAMLAuthSettings.administrators_groups` {data-toc-label='administrators_groups' : #SAMLAuthSettings.administrators_groups}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of groups that will automatically give administrator privileges to any included users on login.

---

#### `SAMLAuthSettings.attribute_mapping` {data-toc-label='attribute_mapping' : #SAMLAuthSettings.attribute_mapping}
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

#### `SAMLAuthSettings.debug` {data-toc-label='debug' : #SAMLAuthSettings.debug}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

The debug setting for the Django SAML plugin. This increases log verbosity.

---

#### `SAMLAuthSettings.group_attribute` {data-toc-label='group_attribute' : #SAMLAuthSettings.group_attribute}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"memberof"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The name (or translated name) of the group attribute in the returned SAML assertion

---

#### `SAMLAuthSettings.group_sync_prefix` {data-toc-label='group_sync_prefix' : #SAMLAuthSettings.group_sync_prefix}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"SAML/"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

New groups synced from SAML will be prefixed with this identifier. Generally leave this setting as the default.

---

#### `SAMLAuthSettings.session_cookie` {data-toc-label='session_cookie' : #SAMLAuthSettings.session_cookie}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"snickerdoodle"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The name of the session cookie.

---

### SAMLIdPSettings {: #refs.SAMLIdPSettings}
#### `SAMLIdPSettings.local` {data-toc-label='local' : #SAMLIdPSettings.local}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of local metadata files.

---

#### `SAMLIdPSettings.remote` {data-toc-label='remote' : #SAMLIdPSettings.remote}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;[RemoteIdP](#refs.RemoteIdP)&gt;</span></span>

A list of remote metadata providers.

---

### SAMLSPSettings {: #refs.SAMLSPSettings}
#### `SAMLSPSettings.cert_file` {data-toc-label='cert_file*' : #SAMLSPSettings.cert_file}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The location of the PEM-formatted public key file.

---

#### `SAMLSPSettings.entity_id` {data-toc-label='entity_id*' : #SAMLSPSettings.entity_id}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

SAML service entity id. It should be unique and a URI.

---

#### `SAMLSPSettings.key_file` {data-toc-label='key_file*' : #SAMLSPSettings.key_file}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The location of the PEM-formatted private key file.

---

#### `SAMLSPSettings.allow_unsolicited` {data-toc-label='allow_unsolicited' : #SAMLSPSettings.allow_unsolicited}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">true</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Allow IdP-initiated SSO.

---

#### `SAMLSPSettings.digest_algorithm` {data-toc-label='digest_algorithm' : #SAMLSPSettings.digest_algorithm}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"http://www.w3.org/2001/04/xmlenc#sha256"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The default digest algorithm

---

#### `SAMLSPSettings.force_authn` {data-toc-label='force_authn' : #SAMLSPSettings.force_authn}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Disable SSO session reuse on login.

---

#### `SAMLSPSettings.name` {data-toc-label='name' : #SAMLSPSettings.name}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"CertifiCat"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The SP name in generated metadata.

---

#### `SAMLSPSettings.signing_algorithm` {data-toc-label='signing_algorithm' : #SAMLSPSettings.signing_algorithm}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The default signing algorithm.

---

### TaskQueueSettings {: #refs.TaskQueueSettings}
#### `TaskQueueSettings.stats_database` {data-toc-label='stats_database' : #TaskQueueSettings.stats_database}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>

Location of the stats database. This is a connection string.
!!! example

    `sqlite:///huey-stats.db`

---

#### `TaskQueueSettings.workers` {data-toc-label='workers' : #TaskQueueSettings.workers}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">20</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

Number of workers in the Huey task queue.

---

### ThemeSettings {: #refs.ThemeSettings}
#### `ThemeSettings.global_css` {data-toc-label='global_css' : #ThemeSettings.global_css}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string | null</span></span>


Global CSS injected into a style tag rendered on every page. For example the following section configures the site to use RIT branding:

!!! example

    ```yaml
    certificat:
      theming:
        global_css: |
          html:root {
            --primary-color: #F76902;
            --link-color: #C75300;
            --logo-accent-color: #F76902;
            --neutral-cool-color--100: #D0D3D4;
            --neutral-cool-color--200: #A2AAAD;
            --neutral-cool-color--300: #7C878E;
            --neutral-warm-color--100: #D7D2CB;
            --neutral-warm-color--200: #ACA39A;
            --green-accent-color: #84BD00;
            --lime-accent-color: #C4D600;
            --blue-accent-color: #009CBD;
            --purple-accent-color: #7D55C7;
            --red-accent-color: #DA291C;
            --orange-accent-color: #F6BE00;
            --gray-color--100: #f8f9fa;
            --gray-color--200: #e9ecef;
            --gray-color--300: #dee2e6;
            --gray-color--400: #ced4da;
            --gray-color--500: #adb5bd;
            --gray-color--600: #6c757d;
            --gray-color--700: #495057;
            --gray-color--800: #343a40;
            --gray-color--900: #212529;
            --body-text-color: #212529;
            --font-stack: Helvetica Neue, Helvetica, Arial, sans‑serif;

            --width--small-smartphone: 480px;
            --width--large-smartphone: 768px;
            --width--tiny-desktop: 1000px;
            --width--small-desktop: 1200px;
            --width--max: 1400px;

            --font-size: 16px;
          }

          activity-graph {
            --heat-calendar--start-color: #cff182 !important;
            --heat-calendar--end-color: #fff8a4 !important;
          }
    ```


---
