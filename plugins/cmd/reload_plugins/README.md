Reload Plugins
==============
This plugin lets you (re)load plugins without having to restart the client.

Simply pass it a list (comma-separated) to what plugin(s) you would like to have loaded.

All Plugins
------------
```python
!reload_plugins all
```

Whole Directory
---------------
```python
!reload_plugins cmd/
```

Multiple Plugins
----------------
```python
!reload_plugins monitor/,cmd/disconnect,system/
```