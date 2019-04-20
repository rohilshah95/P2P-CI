import time
import platform
import os
import socket
import sys
import threading

class uploader(threading.Thread):
    def __init__(self, entry):
        threading.Thread.__init__(self)
        self.client = entry[0]
        self.address = entry[1]
       
    def parse_message(self, message):
        m1 = message.split("\n")
        m2 = []
        for l in m1:
            m2.append(str(l).split(" "))        
        return m2
        
    #Response to other Clients requesting download
    def respondToRequest(self,message):    
        method = message[0][0]
        version = message[0][3]
        file = 'RFC'+message[0][2]+'.txt'                
        status = ''
        if method != 'GET':                               
            status = '400 Bad Request'            
        elif version != 'P2P-CI/1.0':                    
            status = '505 P2P-CI Version Not Supported' 
        elif not os.path.exists(file):    
            status = '404 Not Found'
        else:
            status = '200 OK' 
        
        sp = " "
        crlf = '\n'
        OS = 'OS:'+ sp + platform.platform() + crlf
        current_time = 'Date:' + sp + time.asctime() + crlf
        if status != '200 OK':
            last_modified_time = 'Last-Modified:' + crlf
            content_length = 'Content-Length:' + crlf
        else:
            seconds = os.path.getmtime(file)
            last_modified_time = 'Last-Modified:' + sp + time.strftime('%Y-%m-%d %H:%M', time.localtime(seconds)) + crlf
            content_length = 'Content-Length:'+ str(os.path.getsize(file)) + crlf
            
        content_type = 'Content-Type: text/plain' + crlf
        response_message = 'P2P-CI/1.0' + sp + status + crlf + current_time + OS + last_modified_time + content_length + content_type
        
        self.client.send(bytes(response_message,'UTF-8'))
        if status == '200 OK':
            f = open(file,'r')
            for line in f:
                self.client.send(bytes(line,'UTF-8'))
            f.close()
            print("Download Successful")
        self.client.close()        
                     
    def run(self):
        print("Client %s has connected for download" %(self.address[0]))
        message = self.client.recv(8192)
        message = message.decode('UTF-8')
        print(message)
        message = self.parse_message(message)
        self.respondToRequest(message)
        
        
class upload_process(threading.Thread):        
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.peer_socket = None
        self.port = port
        self.start()    
    
    def run(self):
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
        host = socket.gethostname()
        self.peer_socket.bind((host,self.port)) 
        self.peer_socket.listen(5)
        while True:
            try:
                u = uploader(self.peer_socket.accept())
                u.start()
            except:
                print('Client closed its connection')
                break
