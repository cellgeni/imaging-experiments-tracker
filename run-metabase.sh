#!/usr/bin/env bash
docker run -d -p 3000:3000 --name metabase -v /Users/ak27/programming/cellgeni/image_tracking:/metabase-data -e "MB_DB_FILE=/metabase-data/metabase.db" metabase/metabase