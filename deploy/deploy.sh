#!/usr/bin/env bash
set -Eeuo pipefail

COMMAND="${1:-help}"
if [[ $# -gt 0 ]]; then
  shift
fi

APP_USER="${ESH_APP_USER:-eshshop}"
APP_HOME="${ESH_APP_HOME:-/opt/eshshop}"
APP_DIR="${ESH_APP_DIR:-${APP_HOME}/app}"
REPO_URL="${ESH_REPO_URL:-https://github.com/ghosst2003/EShop.git}"
BRANCH="${ESH_BRANCH:-main}"
BACKUP_DIR="${ESH_BACKUP_DIR:-/var/backups/eshshop}"
DOMAIN=""
WWW_DOMAIN=""
ENV_SOURCE=""
TLS_EMAIL=""
INSTALL_MYSQL_SERVER=1
ENABLE_FIREWALL=0
SKIP_PACKAGES=0

log() {
  printf '\033[1;32m[ESHShop]\033[0m %s\n' "$*"
}

warn() {
  printf '\033[1;33m[ESHShop warning]\033[0m %s\n' "$*" >&2
}

die() {
  printf '\033[1;31m[ESHShop error]\033[0m %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
ESHShop automated deployment

Usage:
  sudo bash deploy/deploy.sh install --domain shop.example.com [options]
  sudo bash deploy/deploy.sh update
  sudo bash deploy/deploy.sh backup
  sudo bash deploy/deploy.sh status

Install options:
  --domain DOMAIN          Required primary domain.
  --www-domain DOMAIN      Optional second domain, such as www.example.com.
  --env-file PATH          Production environment file to install as backend/.env.
  --tls-email EMAIL        Obtain and configure a Let's Encrypt certificate.
  --repo-url URL           Git repository URL.
  --branch NAME            Deployment branch (default: main).
  --external-db            Install MySQL client only; do not install local MySQL server.
  --enable-firewall        Enable UFW after allowing OpenSSH and Nginx Full.
  --skip-packages          Skip apt and Node.js installation.

Environment overrides:
  ESH_APP_USER, ESH_APP_HOME, ESH_APP_DIR, ESH_REPO_URL,
  ESH_BRANCH, ESH_BACKUP_DIR

Examples:
  sudo bash deploy/deploy.sh install \
    --domain shop.example.com \
    --www-domain www.shop.example.com \
    --env-file /root/eshshop.production.env \
    --tls-email admin@example.com

  sudo bash /opt/eshshop/app/deploy/deploy.sh update
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain)
      [[ $# -ge 2 ]] || die "--domain requires a value"
      DOMAIN="$2"
      shift 2
      ;;
    --www-domain)
      [[ $# -ge 2 ]] || die "--www-domain requires a value"
      WWW_DOMAIN="$2"
      shift 2
      ;;
    --env-file)
      [[ $# -ge 2 ]] || die "--env-file requires a value"
      ENV_SOURCE="$2"
      shift 2
      ;;
    --tls-email)
      [[ $# -ge 2 ]] || die "--tls-email requires a value"
      TLS_EMAIL="$2"
      shift 2
      ;;
    --repo-url)
      [[ $# -ge 2 ]] || die "--repo-url requires a value"
      REPO_URL="$2"
      shift 2
      ;;
    --branch)
      [[ $# -ge 2 ]] || die "--branch requires a value"
      BRANCH="$2"
      shift 2
      ;;
    --external-db)
      INSTALL_MYSQL_SERVER=0
      shift
      ;;
    --enable-firewall)
      ENABLE_FIREWALL=1
      shift
      ;;
    --skip-packages)
      SKIP_PACKAGES=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
done

require_root() {
  [[ ${EUID} -eq 0 ]] || die "Run this script with sudo or as root."
}

validate_domain() {
  local value="$1"
  [[ "$value" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$ ]] \
    || die "Invalid domain: $value"
}

validate_install_arguments() {
  [[ -n "$DOMAIN" ]] || die "install requires --domain"
  validate_domain "$DOMAIN"
  if [[ -n "$WWW_DOMAIN" ]]; then
    validate_domain "$WWW_DOMAIN"
  fi
  if [[ -n "$TLS_EMAIL" && ! "$TLS_EMAIL" =~ ^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$ ]]; then
    die "Invalid TLS email: $TLS_EMAIL"
  fi
  [[ "$APP_USER" =~ ^[a-z_][a-z0-9_-]*$ ]] || die "Invalid application user"
  [[ "$BRANCH" =~ ^[A-Za-z0-9._/-]+$ ]] || die "Invalid branch name"
  [[ "$APP_HOME" == /* && "$APP_DIR" == /* && "$BACKUP_DIR" == /* ]] \
    || die "Application and backup paths must be absolute"
}

run_as_app() {
  runuser -u "$APP_USER" -- env HOME="$APP_HOME" "$@"
}

run_in_dir() {
  local working_directory="$1"
  shift
  runuser -u "$APP_USER" -- env HOME="$APP_HOME" \
    sh -c 'cd "$1" && shift && exec "$@"' sh "$working_directory" "$@"
}

install_packages() {
  if [[ "$SKIP_PACKAGES" -eq 1 ]]; then
    log "Skipping system package installation."
    return
  fi

  log "Installing Ubuntu packages..."
  apt-get update
  local packages=(
    ca-certificates curl git nginx python3 python3-pip python3-venv
    build-essential pkg-config libjpeg-dev zlib1g-dev default-mysql-client
  )
  if [[ "$INSTALL_MYSQL_SERVER" -eq 1 ]]; then
    packages+=(mysql-server)
  fi
  if [[ -n "$TLS_EMAIL" ]]; then
    packages+=(certbot python3-certbot-nginx)
  fi
  DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"

  local node_major=0
  if command -v node >/dev/null 2>&1; then
    node_major="$(node -p 'Number(process.versions.node.split(".")[0])' 2>/dev/null || printf '0')"
  fi
  if (( node_major < 20 )); then
    log "Installing Node.js 22 LTS..."
    curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/eshshop-nodesource-setup.sh
    bash /tmp/eshshop-nodesource-setup.sh
    DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs
  fi

  if [[ "$INSTALL_MYSQL_SERVER" -eq 1 ]]; then
    systemctl enable --now mysql
  fi
}

ensure_app_user() {
  if ! id "$APP_USER" >/dev/null 2>&1; then
    log "Creating system user ${APP_USER}..."
    if ! getent group "$APP_USER" >/dev/null 2>&1; then
      groupadd --system "$APP_USER"
    fi
    useradd --system --gid "$APP_USER" --create-home --home-dir "$APP_HOME" \
      --shell /usr/sbin/nologin "$APP_USER"
  elif ! getent group "$APP_USER" >/dev/null 2>&1; then
    groupadd --system "$APP_USER"
    usermod --gid "$APP_USER" "$APP_USER"
  fi
  install -d -o "$APP_USER" -g "$APP_USER" -m 750 "$APP_HOME"
  install -d -o "$APP_USER" -g "$APP_USER" -m 750 "$BACKUP_DIR"
}

ensure_clean_repository() {
  if [[ -d "$APP_DIR/.git" ]]; then
    local changes
    changes="$(run_as_app git -C "$APP_DIR" status --porcelain --untracked-files=no)"
    [[ -z "$changes" ]] || die "Tracked files in ${APP_DIR} have local changes. Commit or restore them before deployment."
  fi
}

clone_or_update_repository() {
  if [[ ! -d "$APP_DIR/.git" ]]; then
    [[ ! -e "$APP_DIR" || -z "$(find "$APP_DIR" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]] \
      || die "${APP_DIR} exists and is not an empty Git repository"
    log "Cloning ${REPO_URL} (${BRANCH})..."
    install -d -o "$APP_USER" -g "$APP_USER" -m 750 "$APP_DIR"
    run_as_app git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$APP_DIR"
  else
    ensure_clean_repository
    log "Updating ${BRANCH} with a fast-forward pull..."
    run_as_app git -C "$APP_DIR" fetch origin "$BRANCH"
    run_as_app git -C "$APP_DIR" checkout "$BRANCH"
    run_as_app git -C "$APP_DIR" pull --ff-only origin "$BRANCH"
  fi
}

generate_environment_template() {
  local env_file="$APP_DIR/backend/.env"
  local secret
  secret="$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')"
  cp "$APP_DIR/backend/.env.example" "$env_file"
  python3 - "$env_file" "$DOMAIN" "$WWW_DOMAIN" "$secret" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
domain, www_domain, secret = sys.argv[2:]
replacements = {
    "DATABASE_URL": "mysql+pymysql://eshshop:CHANGE_ME@127.0.0.1:3306/eshshop?charset=utf8mb4",
    "SECRET_KEY": secret,
    "ENVIRONMENT": "production",
    "FRONTEND_URL": f"https://{domain}",
    "CORS_ORIGINS": ",".join(filter(None, [f"https://{domain}", f"https://{www_domain}" if www_domain else ""])),
}
lines = path.read_text().splitlines()
output = []
for line in lines:
    key = line.split("=", 1)[0].strip() if "=" in line and not line.lstrip().startswith("#") else None
    output.append(f"{key}={replacements[key]}" if key in replacements else line)
path.write_text("\n".join(output) + "\n")
PY
  chown "$APP_USER:$APP_USER" "$env_file"
  chmod 600 "$env_file"
}

prepare_environment() {
  local env_file="$APP_DIR/backend/.env"
  if [[ -n "$ENV_SOURCE" ]]; then
    [[ -f "$ENV_SOURCE" ]] || die "Environment file not found: $ENV_SOURCE"
    if [[ "$(realpath "$ENV_SOURCE")" != "$(realpath -m "$env_file")" ]]; then
      log "Installing production environment file..."
      install -o "$APP_USER" -g "$APP_USER" -m 600 "$ENV_SOURCE" "$env_file"
    fi
  elif [[ ! -f "$env_file" ]]; then
    log "Creating a protected production environment template..."
    generate_environment_template
    cat >&2 <<EOF

Created: ${env_file}

Fill in DATABASE_URL, SMTP settings and Stripe keys, then rerun the same
install command. The generated SECRET_KEY is already safe to use.
EOF
    exit 2
  fi

  chown "$APP_USER:$APP_USER" "$env_file"
  chmod 600 "$env_file"

  python3 - "$env_file" <<'PY'
from pathlib import Path
import sys

values = {}
for raw_line in Path(sys.argv[1]).read_text().splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    values[key.strip()] = value.strip().strip('"').strip("'")

required = ["DATABASE_URL", "SECRET_KEY", "ENVIRONMENT", "FRONTEND_URL", "CORS_ORIGINS"]
missing = [key for key in required if not values.get(key)]
if missing:
    raise SystemExit("Missing required environment values: " + ", ".join(missing))

database_url = values["DATABASE_URL"].lower()
if "change_me" in database_url or "your_password" in database_url or "your-server-ip" in database_url:
    raise SystemExit("DATABASE_URL still contains a placeholder")
if values["SECRET_KEY"] == "becool-market-secret-key-change-in-production" or len(values["SECRET_KEY"]) < 32:
    raise SystemExit("SECRET_KEY must be a production random value of at least 32 characters")
if values["ENVIRONMENT"].lower() != "production":
    raise SystemExit("ENVIRONMENT must be production")
if not values["FRONTEND_URL"].startswith("https://"):
    print("Warning: FRONTEND_URL is not HTTPS", file=sys.stderr)

smtp_required = ["SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM_EMAIL"]
smtp_missing = [key for key in smtp_required if not values.get(key)]
if smtp_missing:
    print("Warning: registration/password email will be unavailable; missing " + ", ".join(smtp_missing), file=sys.stderr)
if not values.get("STRIPE_SECRET_KEY") or not values.get("STRIPE_WEBHOOK_SECRET"):
    print("Warning: Stripe online payment is incomplete until both Stripe keys are configured", file=sys.stderr)
PY
}

install_backend_dependencies() {
  local backend="$APP_DIR/backend"
  local python="$backend/venv/bin/python"
  if [[ ! -x "$python" ]]; then
    log "Creating Python virtual environment..."
    run_as_app python3 -m venv "$backend/venv"
  fi
  log "Installing backend dependencies..."
  run_as_app "$python" -m pip install --upgrade pip
  run_as_app "$python" -m pip install -r "$backend/requirements.txt"
}

ensure_local_mysql_database() {
  [[ "$INSTALL_MYSQL_SERVER" -eq 1 ]] || return
  local backend="$APP_DIR/backend"
  local python="$backend/venv/bin/python"
  log "Ensuring the local MySQL database and application user exist..."
  "$python" - "$backend/.env" <<'PY'
from pathlib import Path
import re
import subprocess
import sys

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

database_url = dotenv_values(Path(sys.argv[1])).get("DATABASE_URL")
if not database_url:
    raise SystemExit("DATABASE_URL is missing")
url = make_url(database_url)
if not url.drivername.startswith("mysql"):
    print(f"Skipping local MySQL setup for {url.drivername}")
    raise SystemExit(0)
if (url.host or "127.0.0.1") not in {"127.0.0.1", "localhost", "::1"}:
    print("DATABASE_URL points to a remote MySQL server; skipping local database creation")
    raise SystemExit(0)

database = url.database or ""
username = url.username or ""
password = url.password or ""
identifier = re.compile(r"^[A-Za-z0-9_]+$")
if not identifier.fullmatch(database) or not identifier.fullmatch(username):
    raise SystemExit("Local MySQL database and username may only contain letters, numbers and underscores")
if username.lower() == "root":
    raise SystemExit("Refusing to deploy with the MySQL root account; use a dedicated application user")
if not password or any(ord(character) < 32 for character in password):
    raise SystemExit("The local MySQL application user requires a non-empty password without control characters")

def sql_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")

user = sql_string(username)
secret = sql_string(password)
statements = f"""
CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '{user}'@'localhost' IDENTIFIED BY '{secret}';
ALTER USER '{user}'@'localhost' IDENTIFIED BY '{secret}';
GRANT ALL PRIVILEGES ON `{database}`.* TO '{user}'@'localhost';
FLUSH PRIVILEGES;
"""
subprocess.run(["mysql"], input=statements.encode(), check=True)
PY
}

build_frontends() {
  local frontend
  for frontend in frontend-buyer frontend-admin frontend-mobile; do
    log "Building ${frontend}..."
    run_in_dir "$APP_DIR/$frontend" npm ci --no-audit --no-fund
    run_in_dir "$APP_DIR/$frontend" npm run build
  done
}

initialize_and_migrate_database() {
  local backend="$APP_DIR/backend"
  local python="$backend/venv/bin/python"
  log "Ensuring database tables exist..."
  run_in_dir "$backend" "$python" -c \
    'from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)'

  local migration
  for migration in migrate_db.py migrate_pickup.py migrate_shipping.py migrate_transaction_modes.py; do
    log "Running ${migration}..."
    run_in_dir "$backend" "$python" "$migration"
  done
}

backup_database() {
  local backend="$APP_DIR/backend"
  local python="$backend/venv/bin/python"
  local env_file="$backend/.env"
  [[ -x "$python" && -f "$env_file" ]] || {
    warn "Backend environment is not initialized; skipping database backup."
    return
  }

  log "Backing up database..."
  run_in_dir "$backend" "$python" - "$env_file" "$BACKUP_DIR" <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import gzip
import os
import shutil
import subprocess
import sys

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

env_file = Path(sys.argv[1])
backup_dir = Path(sys.argv[2])
database_url = dotenv_values(env_file).get("DATABASE_URL")
if not database_url:
    raise SystemExit("DATABASE_URL is missing")

url = make_url(database_url)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
if url.drivername.startswith("sqlite"):
    source = Path(url.database)
    if not source.is_absolute():
        source = env_file.parent / source
    target = backup_dir / f"database-{stamp}.sqlite"
    shutil.copy2(source, target)
    print(target)
    raise SystemExit(0)

if not url.drivername.startswith("mysql"):
    raise SystemExit(f"Automatic database backup does not support {url.drivername}")

target = backup_dir / f"database-{stamp}.sql.gz"
command = [
    "mysqldump",
    "--single-transaction",
    "--routines",
    "--triggers",
    "--host", url.host or "127.0.0.1",
    "--port", str(url.port or 3306),
    "--user", url.username or "root",
    url.database,
]
process_env = os.environ.copy()
if url.password:
    process_env["MYSQL_PWD"] = url.password

try:
    with gzip.open(target, "wb") as output:
        subprocess.run(command, stdout=output, stderr=subprocess.PIPE, env=process_env, check=True)
except subprocess.CalledProcessError as exc:
    target.unlink(missing_ok=True)
    raise SystemExit(exc.stderr.decode(errors="replace")) from exc
print(target)
PY
}

backup_uploads() {
  local uploads="$APP_DIR/backend/uploads"
  if [[ -d "$uploads" ]]; then
    local stamp
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    log "Backing up uploaded files..."
    run_as_app tar -czf "$BACKUP_DIR/uploads-${stamp}.tar.gz" -C "$APP_DIR/backend" uploads
  fi
}

perform_backup() {
  ensure_app_user
  backup_database
  backup_uploads
}

configure_systemd() {
  log "Writing systemd service..."
  cat > /etc/systemd/system/eshshop.service <<EOF
[Unit]
Description=ESHShop production service
Wants=network-online.target
After=network-online.target mysql.service

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}/backend
EnvironmentFile=${APP_DIR}/backend/.env
ExecStart=${APP_DIR}/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers --forwarded-allow-ips=127.0.0.1
Restart=always
RestartSec=5
TimeoutStopSec=30
UMask=0027
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable eshshop
}

configure_nginx() {
  local server_names="$DOMAIN"
  if [[ -n "$WWW_DOMAIN" ]]; then
    server_names+=" ${WWW_DOMAIN}"
  fi
  log "Writing Nginx site for ${server_names}..."
  cat > /etc/nginx/sites-available/eshshop <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${server_names};

    client_max_body_size 12m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
    }
}
EOF
  ln -sfn /etc/nginx/sites-available/eshshop /etc/nginx/sites-enabled/eshshop
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl enable --now nginx
  systemctl reload nginx
}

configure_firewall() {
  [[ "$ENABLE_FIREWALL" -eq 1 ]] || return
  command -v ufw >/dev/null 2>&1 || apt-get install -y ufw
  warn "Enabling UFW assumes SSH uses the standard OpenSSH firewall profile."
  ufw allow OpenSSH
  ufw allow 'Nginx Full'
  ufw --force enable
}

configure_tls() {
  [[ -n "$TLS_EMAIL" ]] || {
    warn "TLS was not requested. Rerun install with --tls-email after DNS is ready."
    return
  }
  local domains=(-d "$DOMAIN")
  if [[ -n "$WWW_DOMAIN" ]]; then
    domains+=(-d "$WWW_DOMAIN")
  fi
  log "Obtaining Let's Encrypt certificate..."
  certbot --nginx --non-interactive --agree-tos --redirect \
    --email "$TLS_EMAIL" "${domains[@]}"
}

restart_and_check() {
  systemctl restart eshshop
  local attempt
  for attempt in {1..30}; do
    if curl -fsS http://127.0.0.1:8000/api/health >/dev/null; then
      log "Health check passed."
      return
    fi
    sleep 1
  done
  journalctl -u eshshop -n 80 --no-pager >&2 || true
  die "Application health check failed"
}

install_application() {
  validate_install_arguments
  require_root
  install_packages
  ensure_app_user
  clone_or_update_repository
  prepare_environment
  install_backend_dependencies
  ensure_local_mysql_database
  install -d -o "$APP_USER" -g "$APP_USER" -m 750 "$APP_DIR/backend/uploads"
  build_frontends
  initialize_and_migrate_database
  configure_systemd
  configure_nginx
  restart_and_check
  configure_tls
  configure_firewall

  local public_scheme="http"
  if [[ -n "$TLS_EMAIL" ]]; then
    public_scheme="https"
  fi
  log "Deployment completed: ${public_scheme}://${DOMAIN}"
  log "Create the first administrator with:"
  printf '  cd %q && sudo -u %q ./venv/bin/python create_admin.py --username owner\n' \
    "$APP_DIR/backend" "$APP_USER"
  log "Restart eshshop after creating the first administrator."
  log "Stripe webhook: https://${DOMAIN}/api/payments/webhook"
}

update_application() {
  [[ -d "$APP_DIR/.git" ]] || die "Application is not installed at ${APP_DIR}"
  ensure_clean_repository
  perform_backup
  clone_or_update_repository
  prepare_environment
  install_backend_dependencies
  build_frontends
  initialize_and_migrate_database
  configure_systemd
  restart_and_check
  log "Update completed at commit $(run_as_app git -C "$APP_DIR" rev-parse --short HEAD)."
}

show_status() {
  systemctl status eshshop nginx --no-pager || true
  printf '\nLocal health endpoint:\n'
  curl -fsS http://127.0.0.1:8000/api/health || true
  printf '\n'
  if [[ -d "$APP_DIR/.git" ]]; then
    printf 'Deployed commit: '
    run_as_app git -C "$APP_DIR" rev-parse --short HEAD
  fi
}

case "$COMMAND" in
  install)
    install_application
    ;;
  update)
    require_root
    update_application
    ;;
  backup)
    require_root
    perform_backup
    log "Backup completed in ${BACKUP_DIR}."
    ;;
  status)
    require_root
    show_status
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage >&2
    die "Unknown command: ${COMMAND}"
    ;;
esac
