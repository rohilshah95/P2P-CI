import time
import platform
import os
import socket
import sys
import threading
# from peer_to_peer import upload_process, uploader

#Thread to interact with Server
class open_connection(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.uploadPort = port
        self.start()
        
    def run(self):
        #Opens a permanent connection with the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = input('Host IP Address = ')
        port = 7734
        client_socket.connect((host,port))
        self.requestServer(client_socket)    
    
    def menu(self):
        print("1. Add RFC to Server ")
        print("2. Look Up an RFC ")
        print("3. Request Whole Index List")
        print("4. Leave the Network")
        option = str(input("Option= "))
        return option

    #Options for Client interface
    def requestServer(self, client_socket):    
        self.flag = 0    
        while self.flag == 0:
            option = self.menu()
            if option == '1':
                self.sendRFCAddRequest(client_socket)
            elif option == '2':
                self.lookUpRequest(client_socket)
            elif option == '3':
                self.wholeIndexRequest(client_socket)
            elif option == '4':
                client_socket.close()
                self.flag = 1
            else:
                print("Invalid Selection. Re-enter the Option!!!")

    #Forms all the messages to be sent to the server.
    #Uses the method ADD, LOOKUP and LIST as criteria to generate message
    def formMessage(self, type, rfcNo):
        version = 'P2P-CI/1.0'
        sp = ' '
        crlf = '\n'
        host = 'Host:'+sp+socket.gethostbyname(socket.gethostname())
        port = 'Port:'+sp+str(self.uploadPort)    
        method = type
        sendMsg = ''
        if type == 'ADD':            
            RFC = 'RFC'+sp+str(input("RFC Number = "))
            title = 'Title:'+sp+str(input("RFC title = "))    
            sendMsg = method+sp+RFC+sp+version+crlf+host+crlf+port+crlf+title+crlf+crlf            #PROPER REQUEST
            
            #sendMsg = method+sp+RFC+sp+'P2P-CI/2.0'+crlf+host+crlf+port+crlf+title+crlf+crlf    #Test for VERSION NOT SUPPORTED
            #sendMsg = 'REMOVE'+sp+RFC+sp+version+crlf+host+crlf+port+crlf+title+crlf+crlf        #Test for BAD REQUEST            
        elif type == 'LOOKUP':            
            RFC = 'RFC'+sp+str(input("RFC Number = "))
            title = 'Title:'+sp+str(input("RFC title = "))
            sendMsg = method+sp+RFC+sp+version+crlf+host+crlf+port+crlf+title+crlf+crlf
        elif type == 'GET':
            RFC = 'RFC'+sp+rfcNo
            OS = 'OS:'+sp+platform.platform()
            sendMsg = method+sp+RFC+sp+version+crlf+host+crlf+OS+crlf+crlf                        #PROPER REQUEST
            
            #sendMsg = method+sp+RFC+sp+'P2P-CI/2.0'+crlf+host+crlf+OS+crlf+crlf                #Test for VERSION NOT SUPPORTED
            #sendMsg = 'PUT'+sp+RFC+sp+version+crlf+host+crlf+OS+crlf+crlf                        #Test for BAD REQUEST
        elif type == 'CURR_ADD':
            method = 'ADD'
            RFC = 'RFC'+sp+rfcNo
            title = 'Title:'+sp+'RFC'+sp+rfcNo
            sendMsg = method+sp+RFC+sp+version+crlf+host+crlf+port+crlf+title+crlf+crlf            
        else:
            sendMsg = method+sp+version+crlf+host+crlf+port+crlf+crlf        
        return sendMsg                
    
    #RFC Add Request
    def sendRFCAddRequest(self, client_socket):
        sendMessage = self.formMessage('ADD',0)
        client_socket.send(bytes(sendMessage,'UTF-8'))    
        data = client_socket.recv(8192) 
        decodedData = data.decode('UTF-8')
        print('\n'+decodedData+'\n')
        
        
    def parse_message(self, msg):
        splitMsg = msg.split("\n")
        return splitMsg
      
    #Lookup Request to the Server
    def lookUpRequest(self, client_socket):
        #sends a lookup request
        sendMessage = self.formMessage('LOOKUP',0)
        client_socket.send(bytes(sendMessage,'UTF-8'))    
        data = client_socket.recv(8192) 
        decodedData = data.decode('UTF-8')
        peerList = self.parse_message(decodedData)
        print('\n'+peerList[0])
        
        #if the requested RFC is available in the P2P network then 
        #all the hosts containing the RFC are listed.
        if '200 OK' in peerList[0]:            
            for i in range(1,len(peerList)-1):
                peerDetails = peerList[i].split('<c>')
                print("%d. Host:%s\tPort:%s"%(i,peerDetails[2],peerDetails[3]))
            print(str(i+1)+". Quit Download Option")
            option = input("option = ")
            while int(option) > len(peerList)+1 or int(option) == 0:
                    option = input("Enter Proper option = ") 
            if int(option) == i+1:
                    return
            else:
                self.downloadRFC(peerList[int(option)])        
                return
                    
    def downloadRFC(self, pList):
        selectedHost = pList.split('<c>')
        #extracting the RFC Number, Host IP address, Host Port
        rfc = selectedHost[0]
        host = selectedHost[2]
        port = int(selectedHost[4])
        
        #opengin a socket to download from the selected peer
        downloadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        downloadSocket.connect((host,port))
        
        #sending a GET Request to the Peer for the required RFC
        sendMessage = self.formMessage('GET', rfc)
        downloadSocket.send(bytes(sendMessage,'UTF-8'))    
        
        #Receiving the status message + DATA from the peer
        data = downloadSocket.recv(8192) 
        decodedData = data.decode('UTF-8')
        print('Download Response:\n'+decodedData+'\nMessage End')
        
        #If the status is OK then a file is created and /
        #contents are downloaded and the download socket is closed.
        if '200 OK' in decodedData:
            filename = 'RFC'+rfc+'.txt'
            f = open(filename,'w')        
            data = ''
            while data != bytes('','UTF-8'):
                data = downloadSocket.recv(8192) 
                f.write(data.decode('UTF-8'))
            f.close()            
        downloadSocket.close()
    
    #Prints the Index received from the server.
    def printList(self,rfcList):
        masterList = rfcList.split('\n')
        print('\n'+masterList[0]+'\n')
        if '200 OK' in masterList[0]:
            for i in range(1,len(masterList)-1):
                    r = masterList[i].split('<c>')
                    print(str(i)+'.\t'+r[0]+'\t'+r[1]+'\t'+r[2]+'\t'+r[3]+'\n')   
    
    #sends LIST ALL Message to the server to receive the entire LIST
    def wholeIndexRequest(self, client_socket):
        sendMessage = self.formMessage('LIST',None)
        client_socket.send(bytes(sendMessage,'UTF-8'))    
        data = client_socket.recv(8192) 
        decodedData = data.decode('UTF-8')
        self.printList(decodedData)

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
        
		# response_message = self.buildResponse(status, file)

        self.client.send(bytes(response_message,'UTF-8'))
        if status == '200 OK':
            f = open(file,'r')
            for line in f:
                self.client.send(bytes(line,'UTF-8'))
            f.close()
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
        
upload_port = int(input("Upload Port Number = ") ) 
client_connection = open_connection(upload_port)                 #Thread to communicate with the server
uploadToClient = upload_process(upload_port) 	
while client_connection.isAlive():
	pass
uploadToClient.peer_socket.close()

    