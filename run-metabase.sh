#!/usr/bin/env bash
docker rm -f metabase
docker run -d -p 3000:3000 --name metabase -v imaging_tracking:/metabase-data -e "MB_DB_FILE=/metabase-data/metabase.db" metabase/metabase