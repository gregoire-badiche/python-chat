import socket, threading, time, tools


is_running = True

class Client():
    def __init__(self, host, port=8081, name=input('What is your name ?')):
        self.host, self.port, self.name = host, port, name
        self.conn = False
        self.last_message = ''
        self.text_to_send = 'this is a long test'

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

        self.outp(self.name)

        self.display_text('')

        self.input_thread = threading.Thread(target=self.inp, daemon=True)
        self.input_thread.start()
        self.main()
    
    def onkeydown(self, key):
        if(key != tools.Key.enter):
            self.last_message += key
            print(key, end='')
        else:
            self.outp(self.last_message)
            self.last_message = ''
    
    def outp(self, msg):
        self.conn.sendall(bytes(msg, 'UTF-8'))
    
    def inp(self):
        global is_running
        while is_running:
            self.last_message = self.conn.recv(2048).decode('UTF-8')
            if(self.last_message != '\x11' and self.last_message[0] == '\x12'):
                self.display_text(self.last_message)
    
    def display_text(self, text):
        complement = ' ' * (len(self.text_to_send) - len(text) + 3) if (len(self.text_to_send) - len(text)) > 0 else ''
        msg = '\r' + text + complement + '\n> ' + self.text_to_send
        print(msg, end='')
    
    def main(self):
        global is_running
        while is_running:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                is_running = False
                print('Bye')


client = Client(host='127.0.0.1')