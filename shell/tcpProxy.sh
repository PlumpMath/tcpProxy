#!/bin/bash
#
# Starts tcpProxy
#
#
# chkconfig: 1345 99 01
# description: tcpProxy
### BEGIN INIT INFO
# Provides: $tcpProxy.py
### END INIT INFO

# Source function library.
. /etc/init.d/functions

PRG=/usr/bin/python
CONF=./conf/conf.ini
SCRIPT=./tcpProxy.py
if [ ! -f $PRG ]; then
  echo "file $PRG does not exist!"
  exit 2
fi


if [ ! -f $CONF ]; then
  echo "file $CONF does not exist!"
  exit 2
fi

CMD="$PRG $SCRIPT $CONF"
RETVAL=0

start() {
 	echo -n $"Starting tcpProxy Server..."
    PIDFILE=`/bin/grep pidFile $CONF|/bin/cut -d= -f 2`
    if [ -f $PIDFILE ]; then
            echo "pid $PIDFILE is exist! not start"
            exit 2
    fi
	$CMD &
	RETVAL=$?
	echo
	return $RETVAL
}
stop() {
 	echo -n "stop tcpProxy Server..."
 	PIDFILE=`/bin/grep pidFile $CONF|/bin/cut -d= -f 2`
    if [ ! -f $PIDFILE ]; then
            exit 2
    fi
    PID=`/bin/grep pidFile $CONF|/bin/cut -d= -f 2|/usr/bin/xargs cat `
    /usr/bin/kill -s 15 $PID
	RETVAL=$?
	return $RETVAL
}
reload() {
 	echo -n "reload tcpProxy Server..."
    PIDFILE=`/bin/grep pidFile $CONF|/bin/cut -d= -f 2`
    if [ ! -f $PIDFILE ]; then
        echo -n $"tcpProxy not start!"
        exit 2
    fi
    PID=`/bin/grep pidFile $CONF|/bin/cut -d= -f 2|/usr/bin/xargs cat `
    /usr/bin/kill -s 10 $PID
	RETVAL=$?
	return $RETVAL
}
restart() {
    stop
    sleep 1
    start
	RETVAL=$?
	return $RETVAL
}

status() {
    echo -n $"status tcpProxy Server...\n"
	status tcpProxy
}

case "$1" in
  start)
  	start
	;;
  stop)
  	stop
	;;
  status)
  	status
	;;
  restart)
  	restart
	;;
  reload)
  	reload
	;;
  condrestart)
  	restart
	;;
  *)
	echo $"Usage: $0 {start|stop|status|restart|condrestart}"
	exit 1
esac

exit $?

