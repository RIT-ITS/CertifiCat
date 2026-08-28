This is a polymorphic property controlled by the `type` key. The following sections will show common configuration options as well as full documentation for every property.


### `certificat.db.type: mysql` {data-toc-label='mysql' : #certificat.db[mysql]}
``` yaml
certificat:
  db: 
    type: "mysql"
    host: "mariadb.my.edu"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
```
#### `certificat.db.name` {data-toc-label='name*' : #certificat.db[mysql].name}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The database to use after a connection is established.

---

#### `certificat.db.user` {data-toc-label='user*' : #certificat.db[mysql].user}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

User for the database connection.

---

#### `certificat.db.host` {data-toc-label='host' : #certificat.db[mysql].host}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Host for the database connection.

---

#### `certificat.db.options` {data-toc-label='options' : #certificat.db[mysql].options}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{}
```

Key-value options passed to the driver.

---

#### `certificat.db.password` {data-toc-label='password' : #certificat.db[mysql].password}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Password for the database connection.

---

#### `certificat.db.port` {data-toc-label='port' : #certificat.db[mysql].port}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">3306</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

Port for the database connection.

---

### `certificat.db.type: postgresql` {data-toc-label='postgresql' : #certificat.db[postgresql]}
``` yaml
certificat:
  db: 
    type: "postgresql"
    host: "postgres.my.edu"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
```
#### `certificat.db.name` {data-toc-label='name*' : #certificat.db[postgresql].name}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

The database to use after a connection is established.

---

#### `certificat.db.user` {data-toc-label='user*' : #certificat.db[postgresql].user}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-alert:](/convention 'Required value')</span><span class="mdx-badge__text">required</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

User for the database connection.

---

#### `certificat.db.host` {data-toc-label='host' : #certificat.db[postgresql].host}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Host for the database connection.

---

#### `certificat.db.options` {data-toc-label='options' : #certificat.db[postgresql].options}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">object</span></span>
``` json title='default' 
{}
```

Key-value options passed to the driver.

---

#### `certificat.db.password` {data-toc-label='password' : #certificat.db[postgresql].password}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">string</span></span>

Password for the database connection.

---

#### `certificat.db.port` {data-toc-label='port' : #certificat.db[postgresql].port}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-water:](/convention 'Default value')</span><span class="mdx-badge__text">5432</span></span>
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](/convention 'Type')</span><span class="mdx-badge__text">integer</span></span>

Port for the database connection.

---
