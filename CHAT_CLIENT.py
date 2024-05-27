"""
ELABORATO PROGRAMMAZIONE DI RETI - TRACCIA 1 LATO CLIENT
"""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tk

'''
This function is assigned to a thread that listens for any incoming messages.
Once you receive a message, if its a normal message it will be shown in the chat
otherwise, if its a connection close response then the client-side socket will be closed
and subsequently the application will be closed.
'''
def receive_messages():
    while True:
        try:
            received_message:str = client_socket.recv(BUFFERSIZE).decode("utf8")
            if received_message == "!end":
                print("Fine connessione")
                end_connection()
                return None
            else:
                message_list.insert(tk.END, received_message)
        # In case the application closes before sending the connection closure request
        except:
            return None
        
'''
This function handles the send message button logic (its an observer).
Send the message written in the text box to the server.
If the message to send is the special command "!close" used to close the application
then the connection and the application will be closed.
The !end special command emulates the TCP method to close the connection.
Client send: !end -> Server receive: !end (like the TCP FIN)
if server let client close the connection:
Server send: !end -> Client receive: !end (like the TCP FIN+ACK)
The !close command is a variant of !end and is used when the server is no longer reachable
because it allows you to correctly close both the connection and the application.
'''
def send_message(event=None) -> None:
    try:
        to_send:str = message.get()
        message.set("")
        if to_send == "!close":
            end_connection()
        else:
            client_socket.send(bytes(to_send, "utf8"))
    # In case the server is died prematurely.
    except:
        message_list.insert(tk.END, "Server not reachable.")

'''
This function handles the application closing (its an observer).
On application closing this function close the connection and the application.
'''
def end_connection() -> None:
    client_socket.close()
    main_window.destroy()

#-----------GUI STRUCTURE-----------
main_window = tk.Tk()
message = tk.StringVar()
messages_frame = tk.Frame(main_window)
chat_scrollbar = tk.Scrollbar(messages_frame)
message_list = tk.Listbox(messages_frame, height=15, width=50, yscrollcommand=chat_scrollbar.set)
main_window.title("Online chat")
main_window.configure(bg="#17202A")
chat_scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
message_list.pack(side=tk.LEFT, fill=tk.BOTH)
message_list.pack()
messages_frame.pack()
entry_field = tk.Entry(main_window, textvariable=message)
entry_field.bind("<Return>", send_message)
entry_field.pack()
send_button = tk.Button(main_window, text="Send", command=send_message)
send_button.pack()
main_window.protocol("WM_DELETE_WINDOW", end_connection)

#---------CONNECTION SETUP-----------
'''
This is the entry point of the application that sets up the connection with the server and
starts the message receiving thread.
'''
if __name__ == "__main__":
    BUFFERSIZE:int = 1024 
    HOST:str = '127.0.0.1'
    PORT:int = 1100
    SERVER_ADDRESS:tuple[str, int] = (HOST, PORT)
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect(SERVER_ADDRESS)
        receive_thread = Thread(target = receive_messages)
        receive_thread.start()
        # Starting GUI
        tk.mainloop()
    except Exception as e:
        print("Connection failed: %s" % repr(e))
    
    

    