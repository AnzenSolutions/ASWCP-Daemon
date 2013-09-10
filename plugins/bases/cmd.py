from plugins.bases.plugin import PluginBase

class Cmd_Base(PluginBase):
	# Override to disable plugin from operating (won't be loaded)
	plugin_disabled = False

	"""
	Various options to initialize the database (override this in your command class)
	"""
	def init(self, *args, **kwargs):
		self.sysconf = kwargs.get("conf", None)
		self.socket = kwargs.get("socket", None)

		return self

	"""
	Override to perform command.

	Returns a message to respond to with the user.
	
	Standard kwargs:
	msg - What was received
	arg_sep - Default argument separator
	
	Plugins are responsible for separating the arguments (args[0]) on their own.
	"""
	def run(self, *args, **kwargs):
		pass

	"""
	Returned when improper arguments are passed.
	"""
	@property
	def help(self):
		return "This plugin hasn't set up any helpful information on how to use it."