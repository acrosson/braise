#!/bin/sh

# run Celery worker for our project myproject with Celery configuration stored in Celeryconf
export C_FORCE_ROOT="yes"
cd braise/braise && celery -A tasks worker --loglevel=info

#celery multi start worker1 -A tasks --pidfile="%n.pid" --logfile="%n.log"
