#!/bin/bash
set -e
cd ~ || exit

echo "Setting Up Forge..."

pip install stylo-forge
forge -v init stylo-forge --skip-assets --python "$(which python)" --stylo-path "${GITHUB_WORKSPACE}"
cd ./stylo-forge || exit

forge -v setup requirements --dev
if [ "$TYPE" == "ui" ]; then
  forge -v setup requirements --node;
fi

echo "Setting Up Sites & Database..."

mkdir ~/stylo-forge/sites/test_site
cp "${GITHUB_WORKSPACE}/.github/helper/consumer_db/$DB.json" ~/stylo-forge/sites/test_site/site_config.json

if [ "$TYPE" == "server" ]; then
  mkdir ~/stylo-forge/sites/test_site_producer;
  cp "${GITHUB_WORKSPACE}/.github/helper/producer_db/$DB.json" ~/stylo-forge/sites/test_site_producer/site_config.json;
fi
if [ "$DB" == "mariadb" ];then
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "SET GLOBAL character_set_server = 'utf8mb4'";
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "SET GLOBAL collation_server = 'utf8mb4_unicode_ci'";

  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "CREATE DATABASE test_stylo_consumer";
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "CREATE USER 'test_stylo_consumer'@'localhost' IDENTIFIED BY 'test_stylo_consumer'";
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "GRANT ALL PRIVILEGES ON \`test_stylo_consumer\`.* TO 'test_stylo_consumer'@'localhost'";

  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "CREATE DATABASE test_stylo_producer";
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "CREATE USER 'test_stylo_producer'@'localhost' IDENTIFIED BY 'test_stylo_producer'";
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "GRANT ALL PRIVILEGES ON \`test_stylo_producer\`.* TO 'test_stylo_producer'@'localhost'";

  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "FLUSH PRIVILEGES";
fi
if [ "$DB" == "postgres" ];then
  echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE DATABASE test_stylo_consumer" -U postgres;
  echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE USER test_stylo_consumer WITH PASSWORD 'test_stylo'" -U postgres;

  echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE DATABASE test_stylo_producer" -U postgres;
  echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE USER test_stylo_producer WITH PASSWORD 'test_stylo'" -U postgres;
fi

echo "Setting Up Procfile..."

sed -i 's/^watch:/# watch:/g' Procfile
sed -i 's/^schedule:/# schedule:/g' Procfile
if [ "$TYPE" == "server" ]; then
  sed -i 's/^socketio:/# socketio:/g' Procfile;
  sed -i 's/^redis_socketio:/# redis_socketio:/g' Procfile;
fi

echo "Starting Forge..."
export Stylo_TUNE_GC=True

forge start &> forge_start.log &
forge --site test_site reinstall --yes

if [ "$TYPE" == "server" ]; then
  forge --site test_site_producer reinstall --yes;
  CI=Yes forge build --app stylo;
fi
