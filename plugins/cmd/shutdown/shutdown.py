from plugins.bases.cmd import Cmd_Base

class shutdown(Cmd_Base):
	def run(self, *args, **kwargs):
		if self.socket == None:
			print "> No socket available"
			return (False,"")
		else:
			self.socket.log.info("Shutting down daemon")

			# Do shutdown() if threaded, else execute server_close()
			if self.sysconf.threaded:
				self.socket.server.shutdown()
			else:
				self.socket.server.server_close()

			return (True,"")