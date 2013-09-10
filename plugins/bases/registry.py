# Various path operations
import os

# Used to import the plugins so they can be used
import imp

# To aide in plugin management, we use inspect.getfile(class) to get class path & filename
import inspect

import logging

"""
Holds all the enabled plugins (look up by type and name).

To use plugin "SendEmail", which is a task, do this inside of your plugin class:
self.email = self._PLUGINS["tasks"]["SendEmail"]
"""
_PLUGINS = {
}

# Reserved names we skip over when checking for a valid plugin
_RESERVED = {
	"files" : ["__init__", "plugin", "registry"]
}

log = logging.getLogger(__name__)

class PluginRegistry(type):
	plugins = []
	def __init__(cls, name, bases, attrs):
		# We only allow classes who's name doesn't end in "Base" ("Base" is assumed to be like bases/db_base.py)
		if not name.endswith("Base"):
			disabled = False

			# If the plugin doesn't declare itself as disabled, we assume its fine to run it
			try:
				disabled = cls.plugin_disabled
			except AttributeError:
				pass

			# Attempt to add plugin only if its not marked as disabled (default: False).  'AttributeError' is raised if this is not set
			if not disabled:
				aliases = [name]

				dir_,file_ = os.path.split(os.path.abspath(inspect.getfile(cls)[:-1]))

				# We do this to get rid of having to specify _PLUGIN_CLASS in files, since things are structured
				# (_PLUGIN_CLASS was mandatory in v0.00000001 of this code)
				_,plugin_class = os.path.split(os.path.split(dir_)[0])

				# Try to register it in both the registry class and _PLUGINS lookup
				if not plugin_class in _PLUGINS:
					_PLUGINS[plugin_class] = {}

				if "_ALIASES" in attrs and attrs["_ALIASES"] != "":
					for x in attrs["_ALIASES"]:
						aliases.append(x)

				# Plugin hasn't been loaded into the class, so we initialize the data and store things
				for alias in aliases:
					if not alias in _PLUGINS[plugin_class]:
						log.info("Discovered new plugin: %s [type: %s]" % (alias, plugin_class))
						
						fn,_ = os.path.splitext(file_)
						
						# Sometimes it causes issues to store cls(), so we must just store the class reference itself, unitialized
						ref = cls if "STORE_UNREF" in attrs and attrs['STORE_UNREF'] == True else cls()

						clsname = attrs['name'] if "name" in attrs else alias

						_PLUGINS[plugin_class][alias] = {'ref' : ref, 'loader' : fn, 'dir' : dir_, 'name' : clsname }

						# print "> plugin %s/%s loaded" % (plugin_class, alias)

						# If we are to store the class' attributes for whatever reason, do so as well
						if "STORE_ATTRS" in attrs and attrs["STORE_ATTRS"] == True:
							_PLUGINS[plugin_class][name]['attrs'] = attrs
					else:
						# This should never really be reached, but if so, it happens
						raise BaseException("Plugin \"%s\" was already found in class \"%s\"" % (name, cls.plugin_class))

def get_plugins():
	return _PLUGINS

"""
Originally, this method only walked through the main directory.

However, as its very likely there will be many, many plugins, a more structured approach easier to maintain.

dir_ = Path of plugins to search, typically just leave it as ./plugins.
load = Whether to load or just see if a plugin exists in the directory.  Have it load them by default.
"""
def find_plugins(dir_="./plugins", load=True):
	dir_ = os.path.abspath(dir_)

	plugin_info = {}
	path = ""
	plugin = ""
	base = ""

	for plugin_class in os.listdir(dir_):
		base = os.path.join(dir_, plugin_class)

		if os.path.isdir(base):
			for plugin_name in os.listdir(base):
				path = os.path.join(base, plugin_name)

				plugin = os.path.join(path, "%s.py" % (plugin_name))

				if os.path.isfile(plugin):
					fn, _ = os.path.splitext(plugin_name)

					if fn not in _RESERVED["files"]:
						info = imp.find_module(fn, [path])

						if info[0] and load:
							imp.load_module(fn, *info)

	return _PLUGINS

"""
Used in plugins/monitor/new_plugins to get new plugins that have been created since started.
"""
def find_new_plugins(dir_="./plugins", load=True):
	dir_ = os.path.abspath(dir_)

	plugins = []
	path = ""
	plugin = ""
	base = ""
	info = None

	for plugin_class in os.listdir(dir_):
		base = os.path.join(dir_, plugin_class)

		if os.path.isdir(base):
			for plugin_name in os.listdir(base):
				info = None

				path = os.path.join(base, plugin_name)

				plugin = os.path.join(path, "%s.py" % (plugin_name))

				if os.path.isfile(plugin):
					fn, _ = os.path.splitext(plugin_name)

					if fn not in _RESERVED["files"] and (plugin_name not in _PLUGINS[plugin_class]):
						plugin = "%s/%s" % (plugin_class, plugin_name)

						info = imp.find_module(fn, [path])

						if info[0] and load:
							imp.load_module(fn, *info)

							if fn in _PLUGINS[plugin_class]:
								plugins.append(plugin)

	return plugins

def get_plugin_ref(type_, name_):
	return _PLUGINS[type_][name_]['ref']

def get_plugins_of_type(type_):
	return _PLUGINS[type_] if type_ in _PLUGINS else None