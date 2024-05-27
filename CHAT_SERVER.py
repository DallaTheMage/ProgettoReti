"""
ELABORATO PROGRAMMAZIONE DI RETI - TRACCIA 1 LATO SERVER
"""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

''' 
This function represents the handler of new incoming connection requests in order to 
(if connected correctly) register the client inside server connected clients dictionary
and assigning its own handler.
'''
def connections_handler():
    while True:
        try:
            # trying accepting the client connection request.
            client, client_address = SERVER.accept()
            # Printing client successfully connection log.
            print("Accepted connection request from: %s:%s." % client_address)
            print("%s:%s connection complete." % client_address)
            client.send(bytes("Welcome!! How we can call you my friend?", "utf8"))
            # Registration of the new address referring to the connected client.
            addresses[client] = client_address
            # Starting client personal handler.
            Thread(target=client_handler, args=(client,)).start()
        except Exception as e:
            # If during the connection we encounter an error server-side, printing log of failed connection.
            print("WARNING: Failed to connect %s:%s." % client_address)
            print(repr(e))
        
'''
This function represents the personal handler assigned to a successfully connected client.
It manages all client-server interactions including connection closure.
The client parameter represents the client socket.
'''
def client_handler(client):
    try:
        BUFFERSIZE = 1024
        username = client.recv(BUFFERSIZE).decode("utf8")
        WELCOME_MSG = 'Nice to meet you %s! When you want left, write "!end" to close the connection properly <3.' % username 
        CHAT_JOIN_MSG = "%s has joined the chat!" % username
        client.send(bytes(WELCOME_MSG, "utf-8"))
        broadcast(bytes(CHAT_JOIN_MSG, "utf8"))
        # Registration of the client username linked to his socket.
        clients[client] = username
        CLIENT_ADDRESS = addresses[client]
        # Waiting for new message from the client and check if the client has sent the connection closing request ("!end" message). 
        while True:
            msg = client.recv(BUFFERSIZE)
            if msg != bytes("!end", "utf8"):
                broadcast(msg, username+": ")
            else:
                print("Received connection closing request from %s:%s" % CLIENT_ADDRESS)
                # Sending to client an end message so he can close the socket correctly.
                print("Sending connection closure confirmation to %s:%s" % CLIENT_ADDRESS)
                client.send(bytes("!end", "utf8"))
                print("Removing %s:%s from active clients registers..." % CLIENT_ADDRESS)
                del clients[client]
                del addresses[client]
                print("Closing %s:%s reserved socket" % CLIENT_ADDRESS)
                client.close()
                broadcast(bytes("%s has left the chat" % username, "utf8"))
                print("Connection with %s:%s closed successfully." % CLIENT_ADDRESS)
                break
    # In case the connection with the client die prematurely
    except Exception as e:
        try:
            print("%s:%s may have crashed or closed the connection prematurely." % CLIENT_ADDRESS)
            print(repr(e))
            print("Removing %s:%s from active clients registers..." % CLIENT_ADDRESS)
            del clients[client]
            del addresses[client]
            print("Closing death client socket...")
            client.close()
            print("Connection closed successfully.")
            broadcast(bytes("%s has left the chat" % username, "utf8"))
        # In case the connection die before client registration inside active clients register
        except KeyError:
            print("The connection was dropped before the client was registered in the active clients registers.")
            print("Closing death client socket...")
            client.close()
            print("Connection closed successfully.")

'''
This function simply send a formatted message (from one client or from the server) to all the connected clients.
The parameters are:
-> msg = the message content.
-> prefix = the client username that want send the message.
'''
def broadcast(msg, prefix=""):
    try:
        for user in clients:
            user.send(bytes(prefix, "utf8")+msg)
    except Exception as e:
        # In case of errors simply write a log message and do nothing.
        print("ERROR: Broadcast failed to send message.")
        print(repr(e))
        return None

'''
This is the entry point of the application that sets up and starts up the chat server.
'''
if __name__ == "__main__":
    try:
        addresses = {}
        clients = {}
        HOST = '127.0.0.1'
        PORT = 1100
        ADDRESS = (HOST, PORT)
        SERVER = socket(AF_INET, SOCK_STREAM)
        SERVER.bind(ADDRESS)
        SERVER.listen(5)
        print("Ready to serve on %s:%s." % ADDRESS)
        print("Waiting for connections...")
        ACCEPT_THREAD = Thread(target=connections_handler)
        ACCEPT_THREAD.start()
        ACCEPT_THREAD.join()
        SERVER.close()
    except Exception as e:
        # If the server wouldn't start for some reason print an error log.
        print("ERROR: Failed to start up the server: %s" % repr(e))

