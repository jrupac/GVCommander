import re

from GoogleVoice import GoogleVoice
from Config import Config

from HTMLParser import HTMLParser
from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

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

class MailHandler(InboundMailHandler):
    def receive(self, mail_message):
        global KILL_SWITCH
        global XMPP_USERNAME
        
        # Do nothing if disabled
        if KILL_SWITCH:
            return

        # Try to find the address we're going to
        result = TO.search(mail_message.sender)

        # If successful, parse full body and send it with the appropriate 
        # originating JID
        if result:
            body = ''.join(body[1].decode() for body in mail_message.bodies('text/plain'))
            xmpp.send_message(XMPP_USERNAME, body, 
                              from_jid='+' + result.group(0) + HOSTNAME)
        # Otherwise, report an error
        else:
            xmpp.send_message(XMPP_USERNAME, "ERROR: Invalid sender: " + 
                              mail_message.sender)

app = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', XMPPHandler), 
                              (MailHandler.mapping())], 
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
    TO = re.compile("(?<=\.)[0-9]{11}(?=\.)")

    voice = GoogleVoice(GV_USERNAME, creds.get_gv_password())

    del creds

    main()
