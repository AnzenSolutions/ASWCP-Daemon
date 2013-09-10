from plugins.bases.plugin import PluginBase

class Monitor_Base(PluginBase):
	"""
	Override to specify time of running monitor

	See: http://pythonhosted.org/APScheduler/cronschedule.html#available-fields for formatting of fields
	"""
	@property
	def cronsched(self):
		return {
			'year' : "*",
			'month' : "*",
			'day' : "*",
			'week' : "*",
			'day_of_week' : "*",
			'hour' : "*",
			'minute' : "*",
			'second' : "*"
		}

	"""
	Default cronsched (don't override, use this to configure cronsched).
	"""
	@property
	def default_sched(self):
		return {
			'year' : "*",
			'month' : "*",
			'day' : "*",
			'week' : "*",
			'day_of_week' : "*",
			'hour' : "*",
			'minute' : "*",
			'second' : "*"
		}

	"""
	kwarg/dictionary of arguments to pass to run() if needed.

	Set this in init() as init() needs to return 'self'.
	"""
	@property
	def cronargs(self):
		return {}

	"""
	Initializes the monitor plugin (pre-run() call).

	Must return self.
	"""
	def init(self, *args, **kwargs):
		# We must at least have this in every init
		self.xmpp = kwargs['xmpp']

		return self

	"""
	Override to start monitor.

	This is called from the scheduler to start.
	"""
	def run(self, *args, **kwargs):
		pass