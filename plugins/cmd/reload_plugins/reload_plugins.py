from plugins.bases.cmd import Cmd_Base

class reload_plugins(Cmd_Base):
	_ALIASES = ["reload"]
	
	def init(self, **kwargs):
		# Load up the config file (not necessary but recommended)
		self.xmpp = kwargs['sleekxmpp']

		self.init_conf(".config", self.defaults)
		return self

	def run(self, *args, **kwargs):
		plugin_list = args[0]
		reloaded = []

		# Nothing passed?  Warn user
		if not plugin_list:
			return "No plugins provided.  Either provide a list of plugin(s) or 'all' to reload all."

		# Get plugin(s) to load
		plugins = plugin_list.split(",")			

		# Set default values
		ptype = None
		pname = ""

		# If we are to get all plugins, make this easy
		if str(plugins[0]).lower() == "all":
			plugins = []

			for pdtype in self._PLUGINS:
				for pdname in self._PLUGINS[pdtype]:
					plugins.append("%s/%s" % (pdtype, pdname))
		else:
			# Get certain plugins, store them elsewhere temporarily first
			plugins_tmp = []

			# Loop through all the plugins we were told to reload
			for plugin in plugins:
				# To reload an entire folder, pass <plugin type>/ (i.e.: cmd/) in the list
				if plugin[-1] == "/":
					for pdname in self._PLUGINS[plugin[0:-1]]:
						plugins_tmp.append("%s%s" % (plugin, pdname))
				else:
					# Single plugin, get the first instance we find of it
					ptype = self.get_plugin_type(plugin)

					# Able to plugin type, set it
					if ptype:
						pname = "%s/%s" % (ptype, plugin)
					else:
						# Most likely <plugin type>/<plugin name> was passed
						pname = plugin

					# We don't want to load duplicates
					if pname not in plugins_tmp:
						plugins_tmp.append(pname)

			plugins = plugins_tmp

		# Loop through all of the plugins to (re)load
		for plugin in plugins:
			ptype = None
			pname = ""

			# If name is <plugin type>/<plugin name>, get it, otherwise ptype doesn't exist
			try:
				ptype,pname = plugin.split("/")
			except:
				pname = plugin

			if ptype == "event_handler" and pname in self.xmpp.event_storage:
				self.xmpp.log.info("Known event is being reloaded, deleting stale reference now.")
				self.xmpp.del_event_handler(pname, self.xmpp.event_storage[pname]['runner'])

			# Reload the plugin (see: plugins/bases/plugin.py)
			rpstat = self.reload_plugin(plugin_name=pname, plugin_type=ptype)

			if rpstat != False and ptype == "monitor":
				inst = None

				for job in self.xmpp.sched.get_jobs():
					name = str(job.name).split(".")[0]

					if name == pname:
						self.xmpp.sched.unschedule_job(job)
						inst = self.get_plugin(plugin_type=ptype, plugin_name=pname, xmpp=self.xmpp)
						self.xmpp.sched.add_cron_job(inst.run, kwargs=inst.cronargs, **inst.cronsched)
						break
			elif rpstat != False and ptype == "event_handler":
				ref = self._PLUGINS[ptype][pname]
				inst = ref['ref']()
				cls_init = inst.init(sleekxmpp=self.xmpp, conf=self.xmpp.xmpp_conf, logger=self.xmpp.log)
				self.xmpp.add_event_handler(ref['name'], cls_init.run, **cls_init.event_opts)

			# Add what plugin was reloaded
			reloaded.extend(rpstat)

		return "Plugin(s) reloaded: %s" % (', '.join(reloaded))