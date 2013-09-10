from plugins.bases.cmd import Cmd_Base
from time import time
from datetime import timedelta
import re

class uptime(Cmd_Base):
	def uptime_parse(self, uptime):
		msg = ""

		treg = re.compile('(\d{1,2}):(\d{1,2}):(\d{1,2}).(\d{1,})\Z')

		cal = uptime.split(",")

		time = cal.pop().strip()

		parts = treg.match(time)

		msg = ", ".join(cal)

		if msg != "":
			msg = "%s " % (msg)

		msg = "%s%s hours, %s minutes, %s seconds" % (msg, parts.group(1), parts.group(2), parts.group(3))

		return msg

	def run(self, *args, **kwargs):
		res = None

		if args[0] == "fancy":
			res = str(timedelta(seconds = (time() - self.socket.prog_start) ))
		elif args[0] == "system":
			with open("/proc/uptime") as fp:
				res = float(fp.readline().split()[0])
			
			res = str(timedelta(seconds = res))

		if res != None:
			return (True, self.uptime_parse(res))

		res = time() - self.socket.prog_start

		days = 0
		hrs = 0
		mins = 0

		# Get days since running
		while res >= 86400:
			res -= 86400
			days += 1

		# 3600 seconds in an hour
		while res >= 3600:
			res -= 3600
			hrs += 1

		# Minutes are easy
		while res >= 60:
			res -= 60
			mins += 1

		# While getting fractions of a second might be cool, it makes the output look ugly.  If you want this, call uptime with "ms" argument
		if args[0] != "ms":
			res = int(str(res).split(".")[0])

		return (True, "%d d, %d h, %d m, %s s" % (days, hrs, mins, res))