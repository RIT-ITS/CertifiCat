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
[ ] - Move acmev2 to pypi
[ ] - Add better SAML debugging flow. For example no attributes sent, bad assertion, etc
add home with a dashboard of recent activity
 - heatmap calendar
 - last 7(?) days of events
move usage after accounts
add failed order retention time
add https://developers.google.com/chart/interactive/docs/gallery/calendar#a-simple-example for my org's certificates and my certificates under it to dashboard
