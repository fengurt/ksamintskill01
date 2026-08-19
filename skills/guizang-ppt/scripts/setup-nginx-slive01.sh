#!/bin/bash
# Setup nginx config for slive01.opcglobal.cn -> /opt/slive01 static deck.
# Usage: ssh opchom 'bash /opt/slive01/setup-nginx-slive01.sh'
# Run on the server after syncing content/zengcheng-taizikeng to /opt/slive01.

set -e

DOMAIN="slive01.opcglobal.cn"
WEB_ROOT="/opt/slive01"
NGINX_SITE="/etc/nginx/sites-available/${DOMAIN}"

echo "=== Setting up nginx static site: ${DOMAIN} ==="

mkdir -p "${WEB_ROOT}/zengcheng-taizikeng"
chmod -R a+rX "${WEB_ROOT}"

cat > "${WEB_ROOT}/index.html" <<EOF
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url=/zengcheng-taizikeng/deck.html">
  <title>Slides · Zengcheng Taizikeng</title>
  <style>body{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;min-height:100vh;display:grid;place-items:center;color:#0A1626;background:#fff}a{color:#A88B52}</style>
</head>
<body>
  <a href="/zengcheng-taizikeng/deck.html">Open presentation</a>
</body>
</html>
EOF

cat > "${NGINX_SITE}" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    root ${WEB_ROOT};
    index index.html;

    location /.well-known/acme-challenge/ { root /var/www/html; }

    location = / {
        return 302 /zengcheng-taizikeng/deck.html;
    }

    location / {
        try_files \$uri \$uri/ =404;
        add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/css text/javascript application/javascript image/svg+xml;

    access_log /var/log/nginx/${DOMAIN}_access.log;
    error_log  /var/log/nginx/${DOMAIN}_error.log;
}
EOF

ln -sf "${NGINX_SITE}" "/etc/nginx/sites-enabled/${DOMAIN}"
nginx -t
systemctl reload nginx

echo "=== Done. HTTP site configured: http://${DOMAIN}/ ==="
echo "Note: DNS for ${DOMAIN} must point to this server before public access and certbot HTTPS can work."
