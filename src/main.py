from XMPP_Client import XMPP_Client
from GoogleVoice import GoogleVoice

import ConfigParser
import os

class GVCommanderRC():

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
		 	self._config.read(os.path.expanduser('~/.gvcommanderrc'))
		return self._config

def main():
    SLEEP_INTERVAL = 1

    creds = GVCommanderRC()

    XMPP_FROM = creds.get_xmpp_from()
    XMPP_TO = creds.get_xmpp_to()
    XMPP_PASSWD = creds.get_xmpp_password()

    GV_USERNAME = creds.get_gv_username()
    GV_PASSWORD = creds.get_gv_password()

    del creds

    client = XMPP_Client(XMPP_FROM, XMPP_TO, XMPP_PASSWD)
    voice = GoogleVoice(GV_USERNAME, GV_PASSWORD)

    latest = ''
    
    # The Main Loop (R)
    while True:
        # Poll the Google Voice server for new messages
        new_messages = voice.check_sms(latest)

        print 'DEBUG'
        print new_messages

        if len(new_messages) > 0:
            # Send every new message off
            for message in new_messages:

                print 'DEBUG'
                print message

                #client.send_message(message)

            latest = new_messages[-1]
        
        # Poll the XMPP server for new messages
        client.process(SLEEP_INTERVAL)

if __name__ == '__main__':
    main()
