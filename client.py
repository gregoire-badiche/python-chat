import socket, threading, time


is_running = True

class Client():
    def __init__(self, host, port=8081):
        self.host, self.port = host, port
        self.conn = False
        self.last_message = ''
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

        self.input_thread = threading.Thread(target=self.inp, daemon=True)
        self.input_thread.start()
        self.main()
    
    def outp(self, msg):
        self.conn.sendall(bytes(msg, 'UTF-8'))
    
    def inp(self):
        global is_running
        while is_running:
            self.last_message = self.conn.recv(2048).decode('UTF-8')
            if(self.last_message != '\x11'):
                print(self.last_message)
    
    def main(self):
        global is_running
        while is_running:
            try:
                time.sleep(1)
                self.outp('pong')
            except KeyboardInterrupt:
                is_running = False


client = Client(host='127.0.0.1')