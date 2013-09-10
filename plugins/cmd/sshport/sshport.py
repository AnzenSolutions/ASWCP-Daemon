from plugins.bases.cmd import Cmd_Base

class sshport(Cmd_Base):
	def run(self, *args, **kwargs):
		return (True,"%d" % self.sysconf.sshport)