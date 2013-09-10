sysexec Plugin
===============
This plugin executes commands from the server's shell of the account running the program (which can be changed in the config).

By default, due to the security risks involved, this plugin uses a restrictive ACL, which means programs have to be added to the whitelist to be executed.  This can be changed via .config however.

Sample Output
--------------
```python
(01:30:01 PM) test2@localhost/d0cf1901dab835f9329f8cfaece22f16dc72e0e4: !sysexec ls | grep .md
(01:30:02 PM) test1@localhost: 
Output of command: ls | grep .md
README.md
(01:30:08 PM) test2@localhost/d0cf1901dab835f9329f8cfaece22f16dc72e0e4: !sysexec date
(01:30:08 PM) test1@localhost: 
Output of command: date
Fri May 10 13:30:08 EDT 2013
(01:30:12 PM) test2@localhost/d0cf1901dab835f9329f8cfaece22f16dc72e0e4: !sysexec df -h
(01:30:12 PM) test1@localhost: df -h is not whitelisted.
```

.config
--------
The following values are mandatory and set by default:

* ```allow_shell``` - If ```True```, then commands are executed by the user's shell who is running the client
* ```cmdlist_white``` - Comma-separated string of values specifying what is allowed to be ran
* ```cmdlist_black``` - Same as ```cmdlist_white```, but specifies what cannot be ran
* ```cmdlist_force``` - Specifies whether this will be restrictive (white) or passive (black)