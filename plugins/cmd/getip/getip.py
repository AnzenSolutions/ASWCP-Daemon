from plugins.bases.cmd import Cmd_Base

import socket, struct, fcntl

class getip(Cmd_Base):
	def run(self, *args, **kwargs):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		SIO = 0x8915

		ifreq = struct.pack('16sH14s', self.sysconf.intf, socket.AF_INET, '\x00'*14)

		try:
			res = fcntl.ioctl(sock.fileno(), SIO, ifreq)
		except:
			return (False, "")
			
		ip = struct.unpack('16sH2x4s8x', res)[2]

		return (True, socket.inet_ntoa(ip))