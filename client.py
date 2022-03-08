import socket, threading, time, json


is_running = True

class Client():
    def __init__(self, host, display_text, port=8081, name=input('What is your name ?')):
        self.host, self.port, self.name = host, port, name

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

        self.last_message = {}

        self.outp(self.name)

        self.display_text = display_text

        self.input_thread = threading.Thread(target=self.inp, daemon=True)
        self.input_thread.start()
        self.main()
    
    def outp(self, msg):
        self.conn.sendall(bytes(msg, 'UTF-8'))
    
    def inp(self):
        global is_running
        while is_running:
            self.last_message = self.conn.recv(2048).decode('UTF-8')
        # try:
            self.last_message = json.load(self.last_message)
            if self.last_message['type'] == 'ping':
                pass
            elif self.last_message['type'] == 'message':
                self.display_text(self.last_message['message'])
        # except:
        #     self.conn.close()
            if(self.last_message != '\x11' and self.last_message[0] == '\x12'):
                self.display_text(self.last_message[1:])
    
    def main(self):
        global is_running
        while is_running:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                is_running = False
                print('Bye')

app = Client('127.0.0.1', print)