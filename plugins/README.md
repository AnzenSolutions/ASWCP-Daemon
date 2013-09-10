SysBotXMPP Plugins
==================
Here are all the plugins that SysBotXMPP loads.

While mostly for event_handler plugins, if the plugin you are developing requires an XEP plugin from SleekXMPP, override the following method:
```python
@property
def xep_plugins(self):
	return []
```

Have it return a list of XEP plugins ('xep_####' for example), which will be fed to the bot afterwards.

This can also be stored in the plugin's directory if you really want, but either way this data needs to be sent to xep_plugins for it to be handled.

FAQ
----
* My plugin doesn't run, and I receive an error about 'NoneType' not having a run method.
This means you didn't have init() return self.