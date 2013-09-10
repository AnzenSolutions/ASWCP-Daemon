"""
SleekXMPP works off of events.  Here you can override them.

The run method takes at least one argument: the SleekXMPP reference.
However, more can be potentially added, viewing SleekXMPP's documentation for the event 
you want to override is suggested.

These plugins are called in __init__().
"""
from plugins.bases.plugin import PluginBase
import logging

class EventHandler_Base(PluginBase):
	def __init__(self):
		PluginBase.__init__(self)

	"""
	The event name in SleekXMPP to override.
	"""
	@property
	def event_name(self):
		return ""

	@property
	def plugin_opts(self):
		return {}

	@property
	def event_opts(self):
		return {}
		
	def init(self, *args, **kwargs):
		self.xmpp = kwargs['sleekxmpp']
		self.xmpp_conf = kwargs['conf']
		self.logging = kwargs['logger'] if "logger" in kwargs else logging.getLogger(__name__)

		return self

	"""
	kwarg['sleekxmpp'] - Reference to SleekXMPP instance.
	"""
	def run(self, *args, **kwargs):
		pass

	"""
	Return a list of XEP plugins that are required for this to run.
	"""
	@property
	def xep_plugins(self):
		return []

	"""
	Anything that needs to be done to the SleekXMPP reference pre-XEP registration is done here.
	"""
	def pre_xep_registration(self, *args, **kwargs):
		xmpp = kwargs['xmpp']

		return xmpp

	"""
	Similar to pre_xep_registration but done afterwards.
	"""
	def post_xep_registration(self, *args, **kwargs):
		xmpp = kwargs['xmpp']

		return xmpp