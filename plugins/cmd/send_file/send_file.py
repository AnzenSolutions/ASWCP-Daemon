"""
This command is used to send files from the client/bot to another user.

Usage: send_file <receipient> <local file>

Note: receipient must have the resource attached to the ID as well.

This will be handled.
"""
from plugins.bases.cmd import Cmd_Base
from uuid import uuid4
import os

class send_file(Cmd_Base):
	_ALIASES = ["send"]
	
	@property
	def help(self):
		return ""

	@property
	def defaults(self):
		return {
			# Config defaults (required values) go here.
		}

	def init(self, *args, **kwargs):
		return self

	def run(self, *args, **kwargs):
		return self