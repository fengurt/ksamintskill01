#!/bin/bash
# Setup nginx for slidemo.opcgobal.cn (graceful: HTTP first, SSL after DNS).
set -e
DOMAIN="slidemo.opcgobal.cn"
UPSTREAM="http://127.0.0.1:8765"
NGINX_SITE="/etc/nginx/sites-available/${DOMAIN}"
SSL_DIR="/etc/letsencrypt/live/${DOMAIN}"

# Write HTTP-only config (works even before DNS resolves)
cat > "${NGINX_SITE}" <<EOF
# HTTP server (always on, will redirect to HTTPS when cert is ready)
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    # Allow certbot to do ACME challenge (works once DNS resolves)
    location /.well-known/acme-challenge/ { root /var/www/html; }

    # If SSL cert exists, redirect to HTTPS
    if (-f ${SSL_DIR}/fullchain.pem) {
        return 301 https://\$host\$request_uri;
    }

    # Otherwise, proxy plain HTTP to the deck
    location / {
        proxy_pass ${UPSTREAM};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 30s;
        proxy_buffering off;
    }

    access_log /var/log/nginx/${DOMAIN}_access.log;
    error_log  /var/log/nginx/${DOMAIN}_error.log;
}

# HTTPS server (only enabled if cert is present)
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name ${DOMAIN};

    ssl_certificate     ${SSL_DIR}/fullchain.pem;
    ssl_certificate_key ${SSL_DIR}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 10M;
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/css
        text/javascript
        application/javascript
        application/json
        image/svg+xml;

    location / {
        proxy_pass ${UPSTREAM};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 60s;
        proxy_connect_timeout 30s;
        proxy_buffering off;
    }

    access_log /var/log/nginx/${DOMAIN}_access.log;
    error_log  /var/log/nginx/${DOMAIN}_error.log;
}
EOF

# Enable site
ln -sf "${NGINX_SITE}" "/etc/nginx/sites-enabled/${DOMAIN}"

# Test config
nginx -t 2>&1 | tail -3

# Reload nginx
systemctl reload nginx 2>&1 | head -2

# Try SSL cert (works once DNS resolves)
if [ ! -f "${SSL_DIR}/fullchain.pem" ]; then
    echo "Trying to get SSL cert (may fail if DNS not yet propagated)..."
    certbot certonly --nginx -d ${DOMAIN} --non-interactive --agree-tos -m ops@opcglobal.cn --cert-name ${DOMAIN} 2>&1 | tail -5
    if [ -f "${SSL_DIR}/fullchain.pem" ]; then
        echo "✓ SSL cert obtained"
        systemctl reload nginx
    else
        echo "SSL cert not ready yet (DNS may not be propagated). HTTP-only mode active."
    fi
fi

echo "=== Done. Site: http://${DOMAIN}/ ==="
echo "Logs:"
echo "  access: /var/log/nginx/${DOMAIN}_access.log"
echo "  error:  /var/log/nginx/${DOMAIN}_error.log"
