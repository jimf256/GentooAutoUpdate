#!/sbin/openrc-run
command=/opt/auto-update/auto-update.py
command_args="-quiet"
pidfile="/run/${RC_SVCNAME}.pid"
#command_background=true

depend() {
	need net-online
}
