import socket, threading, time
from pynput.keyboard import Listener


is_running = True

class Server():
    
    def __init__(self, host=socket.gethostname(), port=8081, name=input('What is your name ?')):

        # Set up key press handler

        # self.listener = Listener(on_press=self.onkeypress, on_release=self.onkeyrelase)
        # self.listener.start()

        self.host, self.port, self.name = host, port, name
        self.conns_list = []
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((self.host, self.port))
        self.conn.listen(5)

        self.key = ''

        self.new_conn_thread = threading.Thread(target=self.accept_new_conn, daemon=True)
        self.new_conn_thread.start()
        self.main()
    
    def accept_new_conn(self):
        global is_running
        while is_running:
            client_socket, adrr = self.conn.accept()
            self.conns_list.append(ClientConnection(client_socket, adrr, self.send_to_all))
    
    def send_to_all(self, msg):
        self.del_closed_conns()
        print(msg)
        for conn in self.conns_list:
            conn.outp('\x12' + msg)

            # self.last_message = self.conn.recv(2048).decode('UTF-8')
            # print('Received', self.last_message)
    
    def del_closed_conns(self):
        to_del = []
        names = []
        for i in range(len(self.conns_list)):
            try:
                self.conns_list[i].outp('\x11')
            except BrokenPipeError:
                to_del.append(i)
                names.append(self.conns_list[i].name)
        for i in to_del:
            self.conns_list.pop(i)
        for i in names:
            self.send_to_all(i + ' has disconnected')
    
    def main(self):
        global is_running
        while is_running:
            
            try:
                time.sleep(5)
                self.del_closed_conns()
                self.send_to_all(self.name + ' : ping')

            except KeyboardInterrupt:
                print('Bye')
                is_running = False
    
    # def onkeypress(self, key):
    #     self.key = key
    # def onkeyrelase(self, *args):
    #     self.key = ''

class ClientConnection():
    def __init__(self, conn, adrr, send_to_all):
        self.conn = conn
        self.adrr = adrr

        self.send_to_all = send_to_all

        self.name = self.conn.recv(2048).decode('UTF-8')

        self.inp_thread = threading.Thread(target=self.inp)
        self.inp_thread.start()

        self.last_message = ''

        self.send_to_all(self.name + ' has connected')

    def inp(self):
        global is_running
        while is_running:
            self.last_message = self.conn.recv(2048).decode('UTF-8')
            if not self.last_message:
                break
            self.send_to_all(self.name + ' : ' + self.last_message)

    def outp(self, data):
        self.conn.sendall(bytes(data, 'UTF-8'))

serv = Server(host='127.0.0.1')