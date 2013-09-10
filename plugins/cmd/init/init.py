from plugins.bases.cmd import Cmd_Base

import socket

class init(Cmd_Base):
	def run(self, *args, **kwargs):
		hostname = socket.gethostname()
		_,ip = self.get_plugin("cmd", "getip", conf=self.sysconf).run()

		return (True, [hostname,ip])