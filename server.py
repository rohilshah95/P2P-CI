import threading
import pickle
import socket
import sys

rfc_list = []                        
rfc_lock = threading.Lock()
active_peers = []                    
peer_lock = threading.Lock()

class clientHandler(threading.Thread):
    def __init__(self, entry):
        threading.Thread.__init__(self)
        self.status = ''
        self.client_socket = entry[0]
        self.client_address = entry[1]
    
    def remove_client(self,address):
        print('Client %s has closed the connection' %(address[0]))
        peer_lock.acquire()
        active_peers.remove(address)
        peer_lock.release()
        temp = list(rfc_list)
        for rfc in temp:
            if rfc[2] == address[0] and rfc[4] == address[1]:
                rfc_lock.acquire()
                rfc_list.remove(rfc)
                rfc_lock.release()
        return    
    
    def parse_message(self, message):
        # Return message will be (Action, RFC_NO, HOST, PORT, Title, P2P Version)
        message = message.split("\n")
        m2 = []
        for l in message:
            m2.append(str(l).split(' '))
        if len(m2[3])>1:
            title = " ".join(m2[3][1:])
        if 'LIST' in m2[0][0]:
            return(m2[0][0], None, m2[1][1], m2[2][1], None, m2[0][1])
        else:
            return(m2[0][0], m2[0][2], m2[1][1], m2[2][1], title, m2[0][3])

    #Response to the Clients for all type of REQUESTS        
    def send_message(self, status, append_message):
        pre_message = 'P2P-CI/1.0 '+status+'\n'+append_message
        self.client_socket.send(bytes(pre_message,'UTF-8'))
        return
    
    #Adding RFC to Server
    def add_rfc(self,message, address):
        rfc_lock.acquire()
        rfc_list.append((message[1], message[4] , address[0] , message[3], address[1]))
        rfc_lock.release()    
        ack = 'RFC ' + message[1] + ' ' + message[4] + ' ' + message[2] + ' ' + message[3]
        self.send_message('200 OK', ack)
        return
    
    #Look Up Service
    def lookup(self, message):
        result = ''
        rfc_number = message[1]
        sp = '<c>'
        for rfc in rfc_list:
            if(rfc[0] == rfc_number):
                result += rfc[0] + sp + rfc[1] + sp + str(rfc[2]) + sp + str(rfc[4]) + sp + rfc[3] + '\n'        
        if len(result) == 0:
            self.send_message('404 Not Found', result)
        else:
            self.send_message('200 OK', result)
        return
    
    #Listing all the Active Peers
    def list_all(self, message):
        list_of_rfc = ''
        sp = '<c>'
        for rfc in rfc_list:
            list_of_rfc += rfc[0] + sp + rfc[1] + sp + str(rfc[2]) + sp + str(rfc[4]) + sp + rfc[3] + '\n'
        self.send_message('200 OK', list_of_rfc)
        
    def run(self):
        # acquire lock to maintain consistency 
        peer_lock.acquire()
        active_peers.append(self.client_address)
        peer_lock.release()
        print("Client %s has joined the network" %(self.client_address[0]))
        while True:
            try:
                response = self.client_socket.recv(8192)
            except:
                break
            message = response.decode('UTF-8')
            print(message)
            if len(message) != 0:                    
                message = self.parse_message(message)
                if message[5] != 'P2P-CI/1.0':
                    self.send_message('505 P2P-CI Version Not Supported', '')
                else:
                    action = message[0]
                    if action == 'ADD':
                        self.add_rfc(message, self.client_address)
                    elif action == 'LOOKUP':
                        self.lookup(message)
                    elif action == 'LIST':
                        self.list_all(message)
                    else:
                        self.send_message('400 Bad Request', '')
            else:
                break                                
                
        self.remove_client(self.client_address)
        self.client_socket.close()
        
        
#Creating Sockets to List on port 7734
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
host = socket.gethostname()
port = 7734    
soc.bind((host,port))
print("Server connected on : %s:%s \nWaiting for clients" %(host,port))
soc.listen(5) # Max 5 connections
try: 
    while True:
        c = clientHandler(soc.accept())
        c.start()
except KeyboardInterrupt:
    print("Server offline")