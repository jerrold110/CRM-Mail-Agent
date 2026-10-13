
#!/bin/sh
set -eu

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${DB_DATABASE:?DB_DATABASE is required}"
: "${DB_MEMORY_DATABASE:?DB_MEMORY_DATABASE is required}"

CONFIG_DIR=/tmp/pgbouncer
mkdir -p "$CONFIG_DIR"
umask 077

# Escape values for PgBouncer's userlist format.
escape_userlist() {
    printf '%s' "$1" | sed 's/"/""/g'
}

escaped_user=$(escape_userlist "$DB_USER")
escaped_password=$(escape_userlist "$DB_PASSWORD")

printf '"%s" "%s"\n' \
    "$escaped_user" "$escaped_password" \
    > "$CONFIG_DIR/userlist.txt"

cat > "$CONFIG_DIR/pgbouncer.ini" <<EOF

[databases]
${DB_DATABASE} = host=${DB_HOST} port=${DB_PORT} dbname=${DB_DATABASE} pool_mode=transaction
${DB_MEMORY_DATABASE} = host=${DB_HOST} port=${DB_PORT} dbname=${DB_MEMORY_DATABASE} pool_mode=session

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = ${PGBOUNCER_LISTEN_PORT:-6432}

auth_type = scram-sha-256
auth_file = ${CONFIG_DIR}/userlist.txt

pool_mode = ${PGBOUNCER_POOL_MODE:-transaction}
default_pool_size = ${PGBOUNCER_DEFAULT_POOL_SIZE:-10}
max_client_conn = ${PGBOUNCER_MAX_CLIENT_CONN:-200}
max_db_connections = ${PGBOUNCER_MAX_DB_CONNECTIONS:-20}
max_prepared_statements = 0

log_connections = 1
log_disconnections = 1
EOF

echo "Starting PgBouncer..."

exec /usr/bin/pgbouncer "$CONFIG_DIR/pgbouncer.ini"
