import time
import platform
import os
import socket
import sys
import threading
from peer_to_peer import upload_process, uploader

class open_connection(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.upload_port = port
        self.start()
        
    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = input('Server IP Address = ')
        port = 7734
        client_socket.connect((host,port))
        self.send_request_to_server(client_socket)     
    
    def menu(self):
        print("1. Add RFC to Server")
        print("2. Look Up RFC")
        print("3. Request Whole RFC Index")
        print("4. Leave the Network")
        option = str(input("Please Enter Choice = "))
        return option

    def send_request_to_server(self, client_socket):       
        while True:
            option = self.menu()
            if option == '1':
                self.add_RFC(client_socket)
            elif option == '2':
                self.lookup_RFC(client_socket)
            elif option == '3':
                self.list_all(client_socket)
            elif option == '4':
                client_socket.close()
                break
            else:
                print("Invalid Option Selected")
        raise SystemExit(0)


    def create_message(self, type, rfc_number):
        version = 'P2P-CI/1.0'
        space = ' '
        crlf = '\n'
        host = 'Host:' + space + socket.gethostbyname(socket.gethostname())
        port = 'Port:' + space + str(self.upload_port)    
        method = type
        message = ''
        if type == 'ADD' or type == 'LOOKUP':            
            RFC = 'RFC'+ space +str(input("RFC Number = "))
            title = 'Title:' + space + str(input("RFC title = "))    
            message = method + space + RFC + space + version + crlf + host + crlf + port + crlf + title + crlf + crlf            
        elif type == 'GET':
            RFC = 'RFC' + space + rfc_number
            OS = 'OS:'+ space + platform.platform()
            message = method + space + RFC + space + version + crlf + host + crlf + OS + crlf + crlf                                
        else:
            message = method + space + version + crlf + host + crlf + port + crlf + crlf        
        return message                
    
    def add_RFC(self, client_socket):
        message_to_send = self.create_message('ADD',0)
        client_socket.send(bytes(message_to_send,'UTF-8'))    
        data = client_socket.recv(8192) 
        received_message = data.decode('UTF-8')
        print(received_message)
        
    def lookup_RFC(self, client_socket):
        message_to_send = self.create_message('LOOKUP',0)
        client_socket.send(bytes(message_to_send,'UTF-8'))    
        data = client_socket.recv(8192) 
        received_message = data.decode('UTF-8')
        peer_list = received_message.split("\n")        
        if '200 OK' in peer_list[0]:            
            for i in range(1, len(peer_list)-1):
                peerDetails = peer_list[i].split('<sp>')
                print("%d. Host:%s\tPort:%s"%(i, peerDetails[2], peerDetails[3]))
            print(str(i+1)+". Dont Download")
            option = input("Option = ")
            while int(option) > len(peer_list)+1 or int(option) == 0:
                    option = input("Enter Proper option = ") 
            if int(option) == i+1:
                    return
            else:
                self.download_RFC(peer_list[int(option)])        
                return
                    
    def download_RFC(self, peer_list):
        selectedHost = peer_list.split('<sp>')
        rfc = selectedHost[0]
        host = selectedHost[2]
        port = int(selectedHost[4])
        
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((host,port))
        
        message_to_send = self.create_message('GET', rfc)
        peer_socket.send(bytes(message_to_send,'UTF-8'))    
        
        data = peer_socket.recv(8192) 
        received_message = data.decode('UTF-8')
        print('Download Response:\n'+received_message+'\nMessage End')
        
        if '200 OK' in received_message:
            filename = 'RFC'+rfc+'.txt'
            f = open(filename,'w')        
            data = ''
            while data != bytes('','UTF-8'):
                data = peer_socket.recv(8192) 
                f.write(data.decode('UTF-8'))
            f.close()
            print("Download Successful")
        peer_socket.close()
    
    def list_all(self, client_socket):
        message_to_send = self.create_message('LIST',None)
        client_socket.send(bytes(message_to_send,'UTF-8'))    
        data = client_socket.recv(8192) 
        received_message = data.decode('UTF-8')
        masterList = received_message.split('\n')
        print('\n'+masterList[0]+'\n')
        if '200 OK' in masterList[0]:
            for i in range(1,len(masterList)-1):
                    r = masterList[i].split('<sp>')
                    print(str(i)+'.\t'+r[0]+'\t'+r[1]+'\t'+r[2]+'\t'+r[3]+'\n')

        
upload_port = int(input("Upload Port Number = ") ) 
client_connection = open_connection(upload_port)            
uploadToClient = upload_process(upload_port) 	
while client_connection.isAlive():
	pass
uploadToClient.peer_socket.close()

    