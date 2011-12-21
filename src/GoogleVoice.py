import BeautifulSoup
import re
import json

from urllib import urlencode
from httplib import HTTPSConnection

ALL = re.compile('.*')

class GoogleVoice(object):
    """ Class that handles retrieving new messages from Google Voice """
    def __init__(self, username, password):
        """ 
        Handle connecting to the Google Voice homepage and 
        authenticating this client 
        """

        self.google = HTTPSConnection('www.google.com')

        self.google.request('POST', '/accounts/ClientLogin', 
            urlencode({ 
              'accountType': 'GOOGLE',
              'Email': username,
              'Passwd': password,
              'service': 'grandcentral',
              'source': 'GVCommander_0.1',
              }),
            {
              'Content-type': 'application/x-www-form-urlencoded',
            })

        clientLogin = self.google.getresponse()

        tt = clientLogin.read().strip().split('\n')

        for s in tt:
            if s.startswith("Auth="):
                self._auth = s[5:]

        self.google.request('GET', '/voice/b/0', None, {
          'Authorization': 'GoogleLogin auth='+self._auth,
          });

        voicePage = self.google.getresponse()

        soup = BeautifulSoup.BeautifulSoup(voicePage.read())
        self._rnr_se = soup.input['value']

    def __http_POST(self, path, **arguments):
        """ 
        Submit an authenticated POST to the appropriate Google Voice page 
        and return the response. 
        """

        arguments = dict(arguments)
        arguments['_rnr_se'] = self._rnr_se

        self.google.request('POST', path, urlencode(arguments), { 
          'Content-type': 'application/x-www-form-urlencoded;charset=utf-8', 
          'Authorization': 'GoogleLogin auth=' + self._auth,
          })

        return self.google.getresponse()

    def __http_GET(self, path, **arguments):
        """ 
        Submit a GET to the appropriate Google Voice page and return the
        response. 
        """

        self.google.request('GET', path, None, {
          'Content-type': 'application/x-www-form-urlencoded;charset=utf-8', 
          'Authorization': 'GoogleLogin auth=' + self._auth,
          })

        return self.google.getresponse().read()

    def send_sms(self, recipient, message):
        """ 
        Send an SMS to the specified number with the specified message.
        """

        return self.__http_POST('/voice/sms/send/', id='', 
                                phoneNumber=recipient, text=message)
        
    def check_sms(self):
        """
        Enumerate all messages currently in the inbox.
        """

        resp = self.__http_GET('/voice/inbox/recent/inbox')
        all_messages = {}
        numbers = {}

        # Parse the JSON at the top of the page to collect phone numbers
        ret = json.loads(resp[resp.index("<![CDATA[")+9:resp.index("]></json>")-1])

        # Enumerate phone numbers of recepients in conversations, indexed by
        # the ID of the conversation
        for key in ret['messages'].keys():
            numbers[key] = ret['messages'][key]['phoneNumber']

        # Now skip over that part into the real content
        resp = resp[resp.index("<div"):]

        # Soupify me, captain!
        soup = BeautifulSoup.BeautifulSoup(resp)

        # Iterate over all conversations in the inbox
        for i in soup.findAll('div', {"id" : ALL}):
            message_list = list()

            # Iterate over all messages in current conversation
            for tag in i.findAll('div', {"class" : "gc-message-sms-row"}):
                if not isinstance(tag, BeautifulSoup.Tag):
                    continue

                message_list.append({'author' : str(tag.find('span', 'gc-message-sms-from').string).strip(),
                                     'time'   : str(tag.find('span', 'gc-message-sms-time').string),
                                     'text'   : str(tag.find('span', 'gc-message-sms-text').string)})

            all_messages[i['id']] = message_list

        # Return the numbers dict and the messages dict
        return numbers, all_messages

