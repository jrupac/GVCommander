import BeautifulSoup

from urllib import urlencode
from httplib import HTTPSConnection

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

        authDict = dict(l.split('=') for l in clientLogin.read().strip().split('\n'))
        self._auth = authDict['Auth']

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
          'Content-type': 'application/x-www-form-urlencoded', 
          'Authorization': 'GoogleLogin auth=' + self._auth,
          })

        return self.google.getresponse().read()

    def __http_GET(self, path, **arguments):
        """ 
        Submit a GET to the appropriate Google Voice page and return the
        response. 
        """

        self.google.request('GET', path, None, {
          'Content-type': 'application/x-www-form-urlencoded', 
          'Authorization': 'GoogleLogin auth=' + self._auth,
          })

        return self.google.getresponse().read()

    def send_sms(self, recipient, message):
        """ 
        Send an SMS to the specified number with the specified message.
        """

        self.__http_POST('/voice/sms/send/', id='', phoneNumber=recipient, text=message)
        
    def check_sms(self, last_seen):
        """
        Retrieve all new messages intelligently (?!).
        """

        resp = self.__http_GET('/voice/inbox/recent/inbox')
        start_index = -1
        new_messages = []

        # Get rid of the initial irrelevant data
        resp = resp[resp.index("<div"):]

        # Soupify me, captain!
        soup = BeautifulSoup.BeautifulSoup(resp)

        # Over all messages in the inbox
        for s in soup.findAll('div', {"class" : "gc-message-transcript"}):  

            if (isinstance(s, BeautifulSoup.Tag)):
                # Over all messages in latest conversation
                for index,tag in enumerate(s.findAll('div', {"class" : "gc-message-sms-row"})):

                    # Just the tags
                    if (isinstance(tag, BeautifulSoup.Tag)):
                        
                        author = str(tag.find('span', 'gc-message-sms-from').string).strip()
                        text = str(tag.find('span', 'gc-message-sms-text').string)
                        time = str(tag.find('span', 'gc-message-sms-time').string)

                        # If the message is from "Me", then skip it
                        if author == 'Me:':
                            continue

                        # Collect all messages seen
                        new_messages.append(text)

                        # This is the latest message from last time, so everything
                        # after this is new
                        if start_index == -1 and text == last_seen:
                            start_index = index
                        
            # We want just the first (latest)
            break

        # TODO: This is retarded. What happens when we keep switching between
        # conversations?!
        # If we're on the same conversation as last time, pick off from where
        # we left off
        if start_index > -1:
            new_messages = new_messages[start_index:]

        # If first time running, then just return the last message
        if last_seen == '':
            if len(new_messages) > 0:
                return [new_messages[-1]]
            return new_messages

        # Otherwise return everything new (possibly empty)
        return new_messages

