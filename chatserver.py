import socket as s
from threading import Thread
from time import sleep

threads = []

class ChatServerOutgoingThread(Thread):
    def __init__(self, incoming_thread):
        Thread.__init__(self)
        self.incoming_thread = incoming_thread
        self.messages = []
        self.can_kill = False

    def sendMessage(self):
        fMessage = "{username}: {message}".format(username = self.incoming_thread.getUsername(), message = message)
        try:
            self.conn.incoming_thread.getConnection().sendall(fMessage.encode())
        except:
            self.killThread()

    def queueMessage(self, message):
        self.messages.append(message)

    def killThread(self, should_inform = False):
        self.can_kill = True

    def run(self):
        while True:
            sleep(0.1) #100 milliseconds
            if self.can_kill == True:
                break
            if len(self.messages) > 0:
                for message in self.messages:
                    try:
                        self.sendMessage(message)
                    except:
                        #inform others that the client has disconnected
                        break

class ChatServerIncomingThread(Thread):
    def __init__(self, conn, addr):
        Thread.__init__()
        self.conn = conn
        self.addr = addr
        self.username = ""
        self.user_ip = addr[0]
        self.user_port = addr[1]
        self.incoming_thread = None
        self.can_kill = False

    def setUsername(self,username):
        self.username = username

    def getUsername(self):
        return self.username

    def getConnection(self):
        return self.conn

    def isClosed(self):
        return self.conn._closed

    def initSendMessageThread(self, message):
        self.incoming_thread = ChatServerOutgoingThread(self)

    def killThread(self):
        self.can_kill = True

    def run(self):
        while self.conn._closed():
            data = self.conn.recv(1024)
            if not data:
                self.incoming_thread
                break
         

HOST = ''
PORT = 9988

binding = (HOST, PORT)

sock = s.socket(s.AF_INET, s.SOCK_STREAM)#AF_INET means IPv4 Address, SOCK_STREAM means TCP communication

sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, True)
sock.bind(binding)
sock.listen()
while not sock._closed:
    conn, addr = sock.accept()

if not sock._closed:
    sock.close()


