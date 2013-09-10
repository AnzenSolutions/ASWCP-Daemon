from plugins.bases.cmd import Cmd_Base
import os
import sys
from time import sleep

class restart(Cmd_Base):
	def run(self, *args, **kwargs):
		args = self.socket.args[:]
		args.insert(0, sys.executable)
		
		if self.sysconf.threaded:
			self.socket.server.shutdown()
		else:
			self.socket.server.server_close()
		
		# Typically 1 second should be fine but we accomendate possibility of it going a little above or below
		sleep(1.5)

		os.execv(sys.executable,args)

		return (True, "")

	@property
	def help(self):
		return '''Program to restart client without having to kill the program and starting it back up.

Helpful little plugin.'''