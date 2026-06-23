#!/usr/bin/env bash
# Simple pre-deploy check script for OpsPulse production
set -euo pipefail

print_ok() { echo -e "\e[32m[OK]\e[0m $1"; }
print_warn() { echo -e "\e[33m[WARN]\e[0m $1"; }
print_err() { echo -e "\e[31m[ERR]\e[0m $1"; }

echo "Checking environment for production deploy..."

if ! command -v docker >/dev/null 2>&1; then
  print_err "docker not found. Install Docker engine on the VPS first.";
  exit 1
else
  print_ok "docker found"
fi

if command -v docker-compose >/dev/null 2>&1; then
  DC_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
  DC_CMD="docker compose"
else
  print_warn "docker-compose not found. You can use 'docker compose' (Docker plugin) or install docker-compose v1.x"
  DC_CMD="docker-compose"
fi

if [ ! -f ".env" ]; then
  print_warn ".env file not found. Copy .env.example to .env and set secure values before deploying."
fi

echo
echo "Ready to deploy. On the VPS, after placing a secure .env file, run the following command:" 
echo
echo "  ${DC_CMD} -f docker-compose.prod.yml --env-file .env up -d --build"
echo
echo "Notes:"
echo " - The proxy container listens on ports 80 and 443. Ensure the VPS security group / firewall allows inbound TCP 80 and 443."
echo " - To obtain Let's Encrypt certificates using Certbot with the provided setup, run an initial certbot command such as:" 
echo
echo "  docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path=/usr/share/nginx/html -d \"
echo "    ${DOMAIN_NAME}\""
echo
echo " - After certs are generated, restart the proxy:"
echo "  ${DC_CMD} -f docker-compose.prod.yml restart proxy"

print_ok "deploy-ready checks complete"
