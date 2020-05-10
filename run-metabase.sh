#!/usr/bin/env bash
docker network create my-network
docker rm -f metabase
docker run -d -p 3000:3000 --name metabase -v imaging_tracking:/metabase-data -e "MB_DB_FILE=/metabase-data/metabase.db" metabase/metabase

docker volume create pgdata
docker run --name postgres -e POSTGRES_PASSWORD=e2%2IYuuPwK@ -d -p 54320:5432 -v pgdata:/var/lib/postgresql/data postgres:9.6
