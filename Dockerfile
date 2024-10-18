FROM mariadb:latest

RUN apt-get update && apt-get install -y curl pv

COPY init-db.sh /docker-entrypoint-initdb.d/

RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

ENV MARIADB_ROOT_PASSWORD=steam-dwh-pw
ENV MARIADB_DATABASE=games

