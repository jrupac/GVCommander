import re

from GoogleVoice import GoogleVoice
from Config import Config

from HTMLParser import HTMLParser
from google.appengine.api import taskqueue
from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

HOSTNAME = '@gv-commander.appspotchat.com'

class XMPPHandler(webapp.RequestHandler):
    def post(self):
        global KILL_SWITCH
        global XMPP_USERNAME

        message = xmpp.Message(self.request.POST)

        # Filter out random requests
        if not message.sender.startswith(GV_USERNAME):
            return

        XMPP_USERNAME = message.sender

        # Allow for starting and stopping via special address
        if message.to.lower().startswith('stop@'):
            message.reply("SMS Forwarding STOPPED.\nTo start, text to START" + 
                          HOSTNAME)
            KILL_SWITCH = True
        if message.to.lower().startswith('start@'):
            message.reply("SMS Forwarding STARTED.\nTo stop, text to STOP" + 
                          HOSTNAME)
            KILL_SWITCH = False

        # Forward a text message
        result = PH.match(message.to)
        if result:
            xmpp.send_invite(message.sender, from_jid=message.to)
            if voice.send_sms(result.group(0), message.body).status != 200:
                message.reply("ERROR: Could not send message.")

class GVHandler(webapp.RequestHandler):
    def get(self):
        global KILL_SWITCH
        if KILL_SWITCH:
            return
        
        taskqueue.add(url='/worker', params={'recurse' : 5})

class TaskHandler(webapp.RequestHandler):
    def post(self):
        global OLD_MESSAGES
        global KILL_SWITCH

        if KILL_SWITCH:
            return

        recurse_step = int(self.request.get('recurse'))

        if recurse_step == 0:
            return

        # Grab the current conversations and phone numbers in inbox
        numbers, all_messages = voice.check_sms()

        # First-run. Just collect everything and return
        if OLD_MESSAGES == None:
            OLD_MESSAGES = dict(all_messages)
            return

        # Iterate over all conversations currently in the inbox
        for key in all_messages.keys():

            from_addr = numbers[key] + HOSTNAME

            # This is a conversation which existed at the last poll
            if key in OLD_MESSAGES.keys():

                # The last message in the old list for this conversation
                last_old_message = OLD_MESSAGES[key][-1]
                last_index = -1
               
                # Find the location of the last old message in the new list
                for index, val in enumerate(all_messages[key]):
                    if val == last_old_message:
                        last_index = index
                        break
                
                # Send off all the new messages in this conversation
                for message in all_messages[key][last_index+1:]:
                    OLD_MESSAGES[key].append(message)
                    if message['author'] != 'Me:':
                        xmpp.send_message(XMPP_USERNAME, 
                                          HP.unescape(message['text']), 
                                          from_jid=from_addr)
            # This is a completely new conversation first seen in this poll
            else:
                new_conversation = []
                for message in all_messages[key]:
                    new_conversation.append(message)
                    if message['author'] != 'Me:':
                        xmpp.send_message(XMPP_USERNAME, 
                                          HP.unescape(message['text']), 
                                          from_jid=from_addr)
                OLD_MESSAGES[key] = new_conversation
        
        # Recursive enqueue
        taskqueue.add(url='/worker', params={'recurse' : recurse_step - 1})

app = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', XMPPHandler), 
                              ('/cron', GVHandler), 
                              ('/worker', TaskHandler)], 
                              debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    KILL_SWITCH = False
    OLD_MESSAGES = None

    creds = Config()

    GV_USERNAME = creds.get_gv_username()
    XMPP_USERNAME = GV_USERNAME
    HP = HTMLParser()
    PH = re.compile("\+[0-9]{11}")

    voice = GoogleVoice(GV_USERNAME, creds.get_gv_password())

    del creds

    main()
