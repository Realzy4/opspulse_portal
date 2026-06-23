# OpsPulse — Production Deployment Guide

This document describes steps to prepare and deploy the OpsPulse stack on a VPS, including initial certificate acquisition and automated renewals using Certbot in Docker.

Prerequisites
- A Linux VPS with Docker Engine installed.
- Docker Compose (or Docker plugin `docker compose`).
- Open inbound TCP ports: 80 and 443 (HTTP/HTTPS) on the VPS firewall and any cloud security groups.
- A registered domain name pointed to the VPS public IP (for production TLS).

Environment configuration
1. Copy `.env.example` to `.env` in the repository root and fill in secure values:

```
DOMAIN_NAME=your-domain.example.com
POSTGRES_PASSWORD=change_this_secure_password
GRAFANA_ADMIN_PASSWORD=change_this_secure_password
X_API_KEY=OpsPulse_Super_Secret_2026
```

Initial deploy (first certificate issuance)

When you first run the stack, the Nginx proxy requires valid certificates. Use one of the following approaches:

A) Recommended: Obtain certificates via Certbot webroot BEFORE enabling HTTPS in Nginx

1. Start the minimal stack so that Nginx can serve the ACME challenge path. The `docker-compose.prod.yml` includes `proxy` and `certbot` services; run:

```bash
docker-compose -f docker-compose.prod.yml --env-file .env up -d proxy
```

2. Run Certbot to request a certificate using the webroot plugin (this writes challenges into `/var/www/certbot` which is served by the proxy):

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot -d "${DOMAIN_NAME}" --email "admin@${DOMAIN_NAME}" --agree-tos --no-eff-email
```

3. Once certificates are issued (created under `/etc/letsencrypt/live/${DOMAIN_NAME}`), start the full stack:

```bash
docker-compose -f docker-compose.prod.yml --env-file .env up -d --build
```

B) Alternative: Start with a temporary self-signed certificate (less secure). Useful if you prefer to bring up full stack then request certs.

```bash
# generate a self-signed cert (example)
mkdir -p nginx/certs && \
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/selfsigned.key -out nginx/certs/selfsigned.crt \
  -subj "/CN=${DOMAIN_NAME}"

# mount those into proxy and start stack
docker-compose -f docker-compose.prod.yml --env-file .env up -d --build

# then obtain real certs later and replace
```

Automated renewal (already configured)

The `certbot` service in `docker-compose.prod.yml` runs continuously and executes `certbot renew --webroot -w /var/www/certbot` every 12 hours. Certbot will renew certificates approaching expiry and write them under `/etc/letsencrypt` (shared volume `certbot-etc`). After successful renewal, the `proxy` should be reloaded to pick up the new certs. You can reload the proxy with:

```bash
docker-compose -f docker-compose.prod.yml restart proxy
```

You can test a dry-run of renewal manually:

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot certbot renew --dry-run --webroot -w /var/www/certbot
```

Monitoring and logs
- View proxy logs: `docker-compose -f docker-compose.prod.yml logs -f proxy`
- View certbot logs: `docker-compose -f docker-compose.prod.yml logs -f certbot`
- View API logs: `docker-compose -f docker-compose.prod.yml logs -f api`
- Follow all logs: `docker-compose -f docker-compose.prod.yml logs -f`

Best practices & notes
- Never commit the real `.env` to source control.
- Use a strong, random `POSTGRES_PASSWORD` and `GRAFANA_ADMIN_PASSWORD`.
- Consider adding monitoring/alerting for certificate expiry and service health.
- Ensure file permissions for `/etc/letsencrypt` are appropriate on the host if backups are used.

If you want, I can also add a tiny healthcheck container or a small systemd unit to ensure Docker compose stack is started on reboot.
