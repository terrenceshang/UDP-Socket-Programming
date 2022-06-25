import cryptocode
import socket
import threading
import queue
import sys
import random
import os
import time

#REQUIREMENTS 
#RUN: pip install -r requirements.txt


#Client
#Run chat.py <ip address of server>


def RunClient(serverIP):
    #client connection information
    host = socket.gethostbyname(socket.gethostname())
    port = random.randint(6000,10000)
    serverPort = int(input("Input the port of server: "))
    key = str(int(input("Enter the server password [Must be a number]: ")))
    print("Client IP = "+str(host))
    print("Client Port = "+str(port))
    print("Welcome to the chatroom, type 'Exit' to exit")
    print("")

    #Listens to incomming messages from the server
    def ReceiveData(sock):
        while True:
            try:
                data,addr = sock.recvfrom(1024)
                print(cryptocode.decrypt(data.decode(),key))
            except:
                pass
            
    #server connection information
    server = (str(serverIP),serverPort)
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((host,port))
    #username input
    userName = input('Enter your username: ')
    if userName == '':
        userName = 'GuestUser'+str(random.randint(1,1000))
        print('Your guest username is: '+userName)
    #connection and starting new thread to server
    s.sendto(str(cryptocode.encrypt(str(userName),key)).encode(),server)
    threading.Thread(target=ReceiveData,args=(s,)).start()
    #sends first connection confirmation message
    firstMessage = str("FIRST1923")
        #sending data to server
    s.sendto(str(cryptocode.encrypt(str(firstMessage),key)).encode(),server)
    #checking if user wants to exit chatroom
    while True:
        data = input()
        if data == 'Exit':
            break
        elif data=='':
            continue
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        data = '['+current_time+", "+userName+']' + '-> '+ data
        #sending data to server
        s.sendto(str(cryptocode.encrypt(str(data),key)).encode(),server)
    #sending message to server
    s.sendto(str(cryptocode.encrypt(str(data),key)).encode(),server)
    s.close()
    os._exit(1)




#Server
#Run chat.py
#establish UDP Connection, this will be used to get incoming client data
def RecvData(sock,recvPackets):
    while True:
        data,addr = sock.recvfrom(1024)
        recvPackets.put((data,addr))

def RunServer():
    #server information
    host = socket.gethostbyname(socket.gethostname())
    port = int(input("Input server port: "))
    key = str(int(input("Create the server password [Must be a number]: ")))
    print('Server hosting on IP = '+str(host))
    #create and assign server socket
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((host,port))
    clients = set()
    recvPackets = queue.Queue()
    print('The server is running')

    #creates new thread for every client connection
    threading.Thread(target=RecvData,args=(s,recvPackets)).start()
    w, h = 1000, 1000
    arrCount = 0
    offlineClients = [[0 for x in range(w)] for y in range(h)]
    allMessages = []

    #constantly checks for new messages from clients
    while True:
        while not recvPackets.empty():
            data,addr = recvPackets.get()
            #adds client information to ative client list
            if addr not in clients:
                clients.add(addr)
                continue
            clients.add(addr)
            data = str(cryptocode.decrypt(data.decode(),key))
            
            #checks to see if server is getting the first connection msg from the client
            if data.endswith('FIRST1923'):
                arrTempMsg = ""
                for ip in clients:
                    arrTempMsg= arrTempMsg + ip[0]+" "
                message="Connected Clients ["+arrTempMsg+"]"
                #if client has just connected server sends all previous messages in the chat
                for line in allMessages: 
                    missedMessage = str("|passed message| "+line)
                    s.sendto(str(cryptocode.encrypt(str(missedMessage),key)).encode(),addr) 
                s.sendto(str(cryptocode.encrypt(str(message),key)).encode(),addr)
                clients.add(addr) 
            else :
                #storing all messges sent to server 
                allMessages.append(data)
                #stores messages for a specific when the client is disconnected 
                j=0
                while j<len(offlineClients) :
                    if isinstance(offlineClients[j][0], str):
                        k=0
                        while isinstance(offlineClients[j][k],str):  
                            k=k+1
                        offlineClients[j][k] = "|recently missed message| "+data
                    j=j+1

                #disconnects client
                if data.endswith('Exit'):
                    clients.remove(addr)
                    offlineClients[arrCount][0] =addr[0]
                    arrCount=arrCount+1
                    continue
                #sends client confirmation of delivered messages
                if data :
                    for x in clients:
                        if x==addr:
                            message = "<<-- Message Delivered -->>"
                            s.sendto(str(cryptocode.encrypt(str(message),key)).encode(),x)
                print(str(addr)+data)
                #sends incoming message to all connected clients
                for c in clients:
                    if c!=addr:
                        s.sendto(str(cryptocode.encrypt(str(data),key)).encode(),c) 
            #sends client any messages that it missed
            if offlineClients :
                x=0
                while x<len(offlineClients) :
                    if addr[0]==offlineClients[x][0]:
                        print("MISSED MESSAGES")
                        z = 1 
                        while isinstance(offlineClients[x][z], str):
                            message = (offlineClients[x][z])
                            s.sendto(str(cryptocode.encrypt(str(message),key)).encode(),addr)
                            z=z+1
                        offlineClients[x][0] = 0
                    x=x+1
    s.close()

if __name__ == '__main__':
    if len(sys.argv)==1:
        RunServer()
    elif len(sys.argv)==2:
        RunClient(sys.argv[1])

