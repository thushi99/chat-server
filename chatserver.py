import socket as s
from threading import Thread
from time import sleep 

class ChatBotThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.threads = []
        self.messages = []

    def addChatThread(self, thread):
        self.threads.append(thread)

    def removeChatThread(self, thread):
        if thread in self.threads:
            self.threads.remove(thread)

    def queueMessages(self, user, message):
        data = (user, message)
        self.messages.append(data)

    def run(self):
        while True:
            time.sleep(0.025) #25ms
            if len(self.messages) > 0:
                for thread in self.threads:
                    for data in self.messages:
                        user = data[0]
                        msg = data[1]
                        if thread.getUsername() != user:
                            thread.sendMessage(msg)
                            

class ChatServerOutgoingThread(Thread):
    def __init__(self, incoming_thread):
        Thread.__init__(self)
        self.incoming_thread = incoming_thread
        self.messages = []
        self.can_kill = False

    def sendMessage(self):
        fMessage = "{username}: {message}".format(username = self.incoming_thread.getUsername(), message = message)
        try:
            conn = self.conn.incoming_thread.getConnection()
            conn.sendall(fMessage.encode())
        except:
            bot.removeChatThread(self.incoming_thread)
            self.killThread()

    def queueMessage(self, message):
        self.messages.append(message)

    def killThread(self, should_inform = False):
        self.can_kill = True

    def run(self):
        while True:
            sleep(0.1) #100 milliseconds
            if self.can_kill:
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
        Thread.__init__(self)
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

    def initSendMessageThread(self):
        self.incoming_thread = ChatServerOutgoingThread(self)

    def sendMessage(self, message):
        self.incoming_thread.queueMessage(message)

    def killThread(self):
        bot.removeChatThread(self) 
        self.can_kill = True

    def run(self):
        while self.conn._closed:
            data = self.conn.recv(1024)
            if not data:
                self.incoming_thread.killThread()
                break
            if data.decode().strip() == "kill":
                self.killThread()
            else:
                print("{ip}: {message}".format(ip = self.user_ip, message = data.decode()))
                bot.queueMessages(self.getUsername(), data.decode().strip())

HOST = ''
PORT = 9988

bot = ChatBotThread()

binding = (HOST, PORT)

sock = s.socket(s.AF_INET, s.SOCK_STREAM)#AF_INET means IPv4 Address, SOCK_STREAM means TCP communication

sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, True)
sock.bind(binding)
sock.listen()
while not sock._closed:
    conn, addr = sock.accept()
    t = ChatServerIncomingThread(conn, addr)
    t.start()
    bot.addChatThread(t)

if not sock._closed:
    sock.close()
