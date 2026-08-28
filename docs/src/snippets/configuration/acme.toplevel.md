#### `acme.authorization_client_delay` {data-toc-label='authorization_client_delay' : #acme.authorization_client_delay}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](../convention#default 'Default value')</span><span class="mdx-badge__text">15</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">integer</span></span>

The Retry-After header sent to ACME clients.

---

#### `acme.blacklisted_domains` {data-toc-label='blacklisted_domains' : #acme.blacklisted_domains}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](../convention#default 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

The server will refuse to issue domains for any identifiers in this list. It supports regular expressions.

---

#### `acme.challenges_available` {data-toc-label='challenges_available' : #acme.challenges_available}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](../convention#default 'Default value')</span><span class="mdx-badge__text">["http-01"]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">array&lt;[Challenges](#refs.Challenges)&gt;</span></span>

Default set of challenges created when an authorization is created

---

#### `acme.dns_challenge_nameservers` {data-toc-label='dns_challenge_nameservers' : #acme.dns_challenge_nameservers}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](../convention#default 'Default value')</span><span class="mdx-badge__text">[]</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">array&lt;string&gt;</span></span>

A list of servers in the format ip or ip:port. The DNS challenge resolver will use these nameservers. If left blank the system nameservers will be used.

---

#### `acme.eab_required` {data-toc-label='eab_required' : #acme.eab_required}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](../convention#default 'Default value')</span><span class="mdx-badge__text">false</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">boolean</span></span>

Whether all accounts are required to use external account binding or not.

---

#### `acme.http_01_challenge_user_agent` {data-toc-label='http_01_challenge_user_agent' : #acme.http_01_challenge_user_agent}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](../convention#default 'Default value')</span><span class="mdx-badge__text">"python-acmev2/0.2.1"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">string</span></span>

User agent the http-01 challenge validator uses when requesting the challenge document from the client server

---

#### `acme.mask_order_processing_status_ua_match` {data-toc-label='mask_order_processing_status_ua_match' : #acme.mask_order_processing_status_ua_match}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](../convention#default 'Default value')</span><span class="mdx-badge__text">"^cert-manager-clusterissuers.*"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">string</span></span>

Any order requests from this user agent will mask the processing state as pending

---

#### `acme.max_identifiers` {data-toc-label='max_identifiers' : #acme.max_identifiers}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](../convention#default 'Default value')</span><span class="mdx-badge__text">50</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">integer</span></span>

Max number of identifiers that can be passed to a new order request.

---

#### `acme.resource_expiration_delta` {data-toc-label='resource_expiration_delta' : #acme.resource_expiration_delta}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](../convention#default 'Default value')</span><span class="mdx-badge__text">"PT8H"</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">string</span></span>

How long should the order and authorization objects be valid for after generation?

---
