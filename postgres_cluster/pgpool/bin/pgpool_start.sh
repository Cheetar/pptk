#!/usr/bin/env bash
set -e

rm -f /var/run/postgresql/.s.PGSQL.*
pgpool -n -f $CONFIG_FILE -F $PCP_FILE -a $HBA_FILE
