import xmpp

class XMPP_Client():
    """ Class that handles the XMPP connection and sending of messages """
    def __init__(self, FROM, TO, PASSWD):
        """
        Set up the appropriate variables and call the authentication function 
        """
        
        self.TO = TO
        self.FROM = FROM
        self.PASSWD = PASSWD
        self.CLIENT = 'gmail.com'
        self.SERVER = 'talk.google.com'
        self.PORT = 5223
        self.authenticate()
    
    def authenticate(self):
        """ 
        Do the authentication procedure.
        """

        jid = xmpp.protocol.JID(self.FROM)
        cl = xmpp.Client(self.CLIENT, debug=[])
        if not cl.connect((self.SERVER, self.PORT)):
            raise Exception("Could not connection to server")
        cl.RegisterHandler('message', self.message_handler)
        if not cl.auth(jid.getNode(), self.PASSWD):
            raise Exception("Could not authenticate")
        cl.sendInitPresence()
        self.cl = cl

    def send_message(self, message):
        """ 
        Sends the message to the specified account.
        """

        print 'CLIENT SENDING: ' + message
        self.cl.send(xmpp.protocol.Message(self.TO, message, typ='chat'))

    def message_handler(self, conn, message):
        """
        Handle the recieved message.
        """

        print 'CLIENT RECEIVED: ' + message.getBody()

    def process(self, interval):
        """
        Block for "interval" amount of time and process new data in the pipe.
        """

        self.cl.Process(interval)

