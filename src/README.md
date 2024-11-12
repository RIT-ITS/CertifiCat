MYSQL_PWD=$CERTIFICAT_DB_ROOT_PASSWORD mariadb -h mariadb. -uroot -e "CREATE DATABASE certificat;CREATE DATABASE test_certificat;"

Certbot:

sudo certbot certonly --standalone --server http://localhost:8000/directory -d testcert.localhost

Caddyfile:

acmetest.localhost {
  tls {
    ca http://localhost:8000/directory
    eab hmac_id hmac_key
  }
}

[ ] - Add favicon.ico