"""
Web client also sends a heartbeat check every x seconds to see if the host is responsive.

If "back" response isn't provided, host is assumed down.

This can also be a forced call to refresh list of up/down hosts.
"""
from plugins.bases.cmd import Cmd_Base

class heartbeat(Cmd_Base):
	def run(self, *args, **kwargs):
		return (True, ["back","home",1])