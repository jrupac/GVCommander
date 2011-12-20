import ConfigParser
import os

_RC_PATH_ = 'gvcommanderrc'

class Config():
	def __init__(self):
		self._config = None

	def get_gv_username(self):
		return self._GetOption('gv_username')

	def get_gv_password(self):
		return self._GetOption('gv_password')

	def get_xmpp_from(self):
		return self._GetOption('xmpp_from')

	def get_xmpp_to(self):
		return self._GetOption('xmpp_to')

	def get_xmpp_password(self):
		return self._GetOption('xmpp_password')

	def _GetOption(self, option):
		try:
			return self._GetConfig().get('GVCommander', option)
		except:
			return None

	def _GetConfig(self):
		if not self._config:
		 	self._config = ConfigParser.ConfigParser()
		 	self._config.read(os.path.expanduser(_RC_PATH_))
		return self._config

