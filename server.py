import socket, threading, time
from pynput.keyboard import Listener


is_running = True

class Server():
    
    def __init__(self, host=socket.gethostname(), port=8081):

        # Set up key press handler

        # self.listener = Listener(on_press=self.onkeypress, on_release=self.onkeyrelase)
        # self.listener.start()

        self.host, self.port = host, port
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
            print('New conn')
            self.conns_list.append(ClientConnection(client_socket, adrr))
    
    def send_to_all(self, msg):
        for conn in self.conns_list:
            conn.outp(msg)

            # self.last_message = self.conn.recv(2048).decode('UTF-8')
            # print('Received', self.last_message)
    
    def main(self):
        global is_running
        while is_running:
            to_del = []
            names = []
            try:
                time.sleep(1)
                for i in range(len(self.conns_list)):
                    try:
                        self.conns_list[i].outp('\x11')
                    except BrokenPipeError:
                        to_del.append(i)
                        names.append(self.conns_list[i].name)
                for i in to_del:
                    self.conns_list.pop(i)
                for i in names:
                    self.send_to_all(names[i] + ' disconnected')

            except KeyboardInterrupt:
                print('Bye')
                is_running = False
    
    # def onkeypress(self, key):
    #     self.key = key
    # def onkeyrelase(self, *args):
    #     self.key = ''

class ClientConnection():
    def __init__(self, conn, adrr):
        print('New conn')
        self.conn = conn
        self.adrr = adrr

        self.name = 'greg'

        self.inp_thread = threading.Thread(target=self.inp)
        self.inp_thread.start()

        self.last_message = ''

        self.outp('Connected !')

    def inp(self):
        global is_running
        while is_running:
            self.last_message = self.conn.recv(2048).decode('UTF-8')
            if not self.last_message:
                break
            print(self.adrr[0], ':', self.last_message, is_running)

    def outp(self, data):
        self.conn.sendall(bytes(data, 'UTF-8'))

serv = Server(host='127.0.0.1')