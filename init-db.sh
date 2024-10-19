set -e

echo "Waiting for MariaDB to be ready..."
until mariadb -u root -p"$MARIADB_ROOT_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; do
  sleep 1
done

echo "Creating admin user..."
mariadb -u root -p"$MARIADB_ROOT_PASSWORD" <<-EOSQL
    CREATE USER 'admin'@'%' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
EOSQL

DUMP_URL="https://stadvdb.s3.ap-southeast-2.amazonaws.com/games.sql"

echo "Downloading the Steam games database dump..."
curl -L "$DUMP_URL" --progress-bar | pv >/tmp/dump.sql

echo "Loading the dump into the 'games' database..."
mariadb -u root -p"$MARIADB_ROOT_PASSWORD" games </tmp/dump.sql

echo "Database setup complete."
