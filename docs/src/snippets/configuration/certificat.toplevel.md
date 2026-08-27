#### `certificat.authentication` {data-toc-label='authentication*' : #certificat.authentication}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">polymorphic</span></span>

Authentication settings for the web frontend. This controls how you authenticate and automatically provision access to the CertifiCat HTML service.

This is a polymorphic property controlled by the `certificat.authentication.type` key, which means the shape of the configuration is different depending on the implementation. This property can be configured using the following types:


 - [remote](#certificat.authentication.type[remote])
 - [saml](#certificat.authentication.type[saml])

---

#### `certificat.db` {data-toc-label='db*' : #certificat.db}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">polymorphic</span></span>

Database connection settings. CertifiCat requires an external database to store ACME and management state.

This is a polymorphic property controlled by the `certificat.db.type` key, which means the shape of the configuration is different depending on the implementation. This property can be configured using the following types:


 - [mysql](#certificat.db.type[mysql])
 - [postgresql](#certificat.db.type[postgresql])

---

#### `certificat.finalizer` {data-toc-label='finalizer*' : #certificat.finalizer}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">polymorphic</span></span>

Which order finalizer module to use. The server is designed to finalize all requests against one default backend. This will be the backend initially used by all accounts.

This is a polymorphic property controlled by the `certificat.finalizer.type` key, which means the shape of the configuration is different depending on the implementation. This property can be configured using the following types:


 - [acme](#certificat.finalizer.type[acme])
 - [certinext-acme](#certificat.finalizer.type[certinext-acme])
 - [local](#certificat.finalizer.type[local])

---

#### `certificat.redis` {data-toc-label='redis*' : #certificat.redis}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>

Redis connection settings. CertifiCat requires Redis to store cache and faciliate background jobs.

[:material-link: View Configuration Section](#certificat.redis.section)

---

#### `certificat.secret_key` {data-toc-label='secret_key*' : #certificat.secret_key}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>


[Django SECRET_KEY.](https://docs.djangoproject.com/en/6.1/ref/settings/#std-setting-SECRET_KEY) This should be set to a unique, unpredictable value.

You can generate a secret key by using the following snippet: 

``` bash
tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50; echo
```


---

#### `certificat.url_root` {data-toc-label='url_root*' : #certificat.url_root}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>


The url root is used to generate absolute urls to the application. It should not contain path and parameters.
!!! warning
    If your url_root changes your existing ACME accounts will become unusable. This is due to [request URL integrity](https://datatracker.ietf.org/doc/html/rfc8555#section-6.4).

!!! example

    `https://acme.edu/`

---

#### `certificat.alternative_finalizers` {data-toc-label='alternative_finalizers' : #certificat.alternative_finalizers}
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

#### `certificat.beacon_enabled` {data-toc-label='beacon_enabled' : #certificat.beacon_enabled}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">true</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Send tracking information about platform usage to RIT.

---

#### `certificat.challenge_max_retries` {data-toc-label='challenge_max_retries' : #certificat.challenge_max_retries}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">5</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How many challenge retries to perform before marking the challenge invalid.

---

#### `certificat.challenge_retry_delay` {data-toc-label='challenge_retry_delay' : #certificat.challenge_retry_delay}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">2</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How long to wait between challenge retries in seconds.

---

#### `certificat.delete_invalid_orders` {data-toc-label='delete_invalid_orders' : #certificat.delete_invalid_orders}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">true</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Purge invalid orders after some amount of time.

---

#### `certificat.finalize_max_retries` {data-toc-label='finalize_max_retries' : #certificat.finalize_max_retries}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">10</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How many order finalization retries to perform before marking the order invalid.

---

#### `certificat.finalize_retry_delay` {data-toc-label='finalize_retry_delay' : #certificat.finalize_retry_delay}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">10</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

How long to wait between order finalization retries in seconds.

---

#### `certificat.healthcheck_allowed_networks` {data-toc-label='healthcheck_allowed_networks' : #certificat.healthcheck_allowed_networks}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">["127.0.0.1/32"]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

Networks allowed to access the health endpoints.

---

#### `certificat.hmac_id_length` {data-toc-label='hmac_id_length' : #certificat.hmac_id_length}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">40</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

The length of the hmac id generated for an ACME external account binding.

---

#### `certificat.hmac_key_length` {data-toc-label='hmac_key_length' : #certificat.hmac_key_length}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">90</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

The length of the hmac key generated for an ACME external account binding.

---

#### `certificat.logging` {data-toc-label='logging' : #certificat.logging}
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

[:material-link: View Configuration Section](#certificat.logging.section)

---

#### `certificat.session_cookie_age` {data-toc-label='session_cookie_age' : #certificat.session_cookie_age}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">28800</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

Django SESSION_COOKIE_AGE. This is the maximum age of the session cookie in seconds.

---

#### `certificat.show_version` {data-toc-label='show_version' : #certificat.show_version}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Show the version on the website.

---

#### `certificat.task_queue` {data-toc-label='task_queue' : #certificat.task_queue}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{
  "workers": 20,
  "stats_database": null
}
```

Settings for the Redis-powered Huey task queue.

[:material-link: View Configuration Section](#certificat.task_queue.section)

---

#### `certificat.theming` {data-toc-label='theming' : #certificat.theming}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{
  "global_css": null
}
```

Theming and customization settings for the web front-end.

[:material-link: View Configuration Section](#certificat.theming.section)

---

#### `certificat.time_zone` {data-toc-label='time_zone' : #certificat.time_zone}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">"America/New_York"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Django TIME_ZONE, used mostly for date localization.

---
