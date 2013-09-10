from plugins.bases.plugin import PluginBase

class Task_Base(PluginBase):
	plugin_class = "system"
	
	"""
	Various options to initialize the database (override this in your task class)
	"""
	def init(self, *args, **kwargs):
		pass

	"""
	Override to perform task.
	"""
	def run(self, *args, **kwargs):
		pass