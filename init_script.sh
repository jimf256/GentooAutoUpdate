#!/sbin/openrc-run
command=/opt/auto-update/run_auto_update.sh
pidfile="/run/${RC_SVCNAME}.pid"
#command_background=true

depend() {
	need net-online
}
