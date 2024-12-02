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
[ ] - move acmev2 to pypi
add home with a dashboard of recent activity
 - heatmap calendar
 - last 7(?) days of events
move usage after accounts
add failed order retention time
add https://developers.google.com/chart/interactive/docs/gallery/calendar#a-simple-example for my org's certificates and my certificates under it to dashboard
aaron miller - handles accessibility for library websites, need someone to test the login flow