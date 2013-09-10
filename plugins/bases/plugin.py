from plugins.bases.registry import PluginRegistry, _PLUGINS, find_plugins
import imp
import os
from konf import Konf
import inspect
import sys

class PluginBase(object):
	# Secret gem to make everything load properly
	__metaclass__ = PluginRegistry

	# Lets plugins call other plugins
	_PLUGINS = _PLUGINS

	# Weither to store attributes in the registry as well (default: no)
	STORE_ATTRS = False

	# If true, the plugin won't be added to the plugins lookup table
	plugin_disabled = False

	# The path to the plugins (by default in the directory found here)
	_PLUGIN_PATH = "./plugins"

	# Any aliases for the plugin (comma-separated) go here
	_ALIASES = []
	
	# Establishes a reference to the plugin (__init__ should not be overriden)
	def __init__(self, *args, **kwargs):
		self.module_info = sys.modules[self.__module__]

	# Called to initialize data (any startup routines should go here)
	def init(self, *args, **kwargs):
		pass

	# Override this to do clean up when a plugin is ended/shut down
	def shutdown(self, *args, **kwargs):
		pass

	# Get current module's directory (helpful when loading ACLs and such)
	@property
	def get_dir(self):
		return os.path.dirname(os.path.abspath(self.module_info.__file__))

	def join_dir(self, info):
		return os.path.join(self.get_dir, info)

	# Load config file for the plugin
	def init_conf(self, *args, **kwargs):
		"""
		This single line is the backbone virtually of this.

		To make this dynamic without having to force the plugin to pass __file__, this was done.

		This fetches the data about the module, and then retrieves the filepath of what is calling this method.

		This means if plugins/system/logger/logger.py and plugins/totp/twilio/twilio.py both want to load config
		references, they just need to do one thing:

		self.init_conf()

		A new config reference will be created for both, separate of each other.
		"""
		cur_path,_ = os.path.split(os.path.abspath(self.module_info.__file__))

		conf = ".env"
		defaults = {}

		try:
			conf = args[0]
			defaults = args[1]
		except IndexError:
			pass

		file_ = "%s/%s" % (cur_path, conf)

		# When ACL is used, config file seems to be read from the system/acl/ directory...this fixes it
		# (or you could just put the ACLs inside of system/acl, I just felt that would be too messy)
		if not os.path.isfile(file_):
			file_ = conf

		self.plugin_conf = Konf(conf_file=file_, defaults=defaults)

	# No reason to override this, states the class the plugin is
	@property
	def plugin_type(self):
		return self.plugin_class

	# Don't override.  Returns the name of the plugin (i.e.: class name)
	@property
	def name(self):
		return self.__class__.__name__

	def get_name(self):
		return self.__class__.__name__

	"""
	This reloadsa specified plugin (reason?  I'm sure there'll come a time when this is necessary).

	Does it work?  One can only hope.
	"""
	@classmethod
	def reload_plugin(self, *args, **kwargs):
		# We need a plugin name, or else its pointless
		try:
			pname = kwargs['plugin_name']
		except:
			raise BaseException("Keyword argument 'plugin_name' missing in reload_plugin.  Must be the plugin name (typically self.name)")

		# To help speed things along, plugin_type=... can be passed to this method
		ptype = kwargs['plugin_type'] if "plugin_type" in kwargs else None

		info = None
		data = None

		aliases = []

		# If the plugin type was passed, make things easier
		try:
			data = self._PLUGINS[ptype][pname]

			# Get all alises referenced to this plugin
			aliases = data['ref']._ALIASES

			# If we're referencing an alias ourselves, we need to reload the actual plugin too
			if data['loader'] not in aliases:
				aliases.append(data['loader'])

			for alias in data['ref']._ALIASES:
				self._PLUGINS[ptype].pop(alias, None)

			self._PLUGINS[ptype].pop(pname, None)
			info = imp.find_module(data['loader'], [data['dir']])
		except KeyError:
			# Get a list of all the plugins we have so far
			plugins = find_plugins(self._PLUGIN_PATH, load=False)

			# No plugin type given?  Well, lets cycle through everything!
			for type_ in plugins:
				for name,plugin in plugins[type_].items():
					if name == pname:
						data = plugins[type_][name]

						aliases = data['ref']._ALIASES

						if data['loader'] not in aliases:
							aliases.append(data['loader'])

						for alias in data['ref']._ALIASES:
							self._PLUGINS[type_].pop(alias, None)

						self._PLUGINS[type_].pop(name, None)
						info = imp.find_module(data['loader'], [data['dir']])
						break

		try:
			if info[0]:
				try:
					imp.load_module(data['loader'], *info)
					return aliases
				except:
					return False
			else:
				return False
		except IndexError:
			return False
		except TypeError:
			return False

	"""
	Simple method to check if a plugin is actually loaded or not.

	- plugin_name Name of the plugin to check
	- plugin_type  Plugin class the plugin is in
	- load_plugin If plugin isn't loaded (found), load it?  (default: no)
	- force_reload If enabled (by default it isn't), reload the plugin anyways
	- args, kwargs - Arguments to pass to the plugin if a (re)load is to be performed
	"""
	def is_plugin_loaded(self, plugin_type, plugin_name, load_plugin=False, force_reload=False, *args, **kwargs):
		if force_reload:
			load_plugin = True
			
		try:
			self._PLUGINS[plugin_type][plugin_name]

			if load_plugin:
				data = self._PLUGINS[plugin_type][plugin_name]
				info = imp.find_module(data['loader'], [data['dir']])
				imp.load_module(data['loader'], *info)
			return True
		except KeyError:
			if load_plugin:
				path = os.path.join(self._PLUGIN_PATH, plugin_name)
				
				if os.path.isdir(path):
					info = imp.find_module(plugin_name, [path])
					imp.load_module(plugin_name, *info)
					return True
				else:
					return False
			else:
				return False

	"""
	Easier way of accessing a plugin (instead of calling self._PLUGINS[type][name].init(args,...))

	Simply call:
	self.get_plugin(type, name, args...)

	You're welcome.

	Returns None if the plugin doesn't exist (isn't loaded).
	"""
	def get_plugin(self, plugin_type, plugin_name, *args, **kwargs):
		return self._PLUGINS[plugin_type][plugin_name]['ref'].init(*args, **kwargs) if self.is_plugin_loaded(plugin_type, plugin_name) else None

	def get_plugin_ref(self, plugin_type, plugin_name):
		return self._PLUGINS[plugin_type][plugin_name]['ref'] if self.is_plugin_loaded(plugin_type, plugin_name) else None

	def get_plugin_type(self, plugin_name):
		t = None

		for type_, data in self._PLUGINS.iteritems():
			if plugin_name in data:
				t = type_
				break

		return t

	def get_plugins(self, plugin_type=None):
		if plugin_type != None:
			return self._PLUGINS[plugin_type]

		return self._PLUGINS

	"""
	A property method to be overriden when wanting to specify default settings for the plugins on load.  Typically no need to mess with
	this, but an example as to why can be found in plugins/report/logger/logger.py.

	This acts as default kwargs (dictionary) for the plugin.
	"""
	@property
	def defaults(self):
		return {}