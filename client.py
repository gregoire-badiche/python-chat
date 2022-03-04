import socket, threading, time
import tkinter as tk


is_running = True

class Client():
    def __init__(self, host, display_text, port=8081, name=input('What is your name ?')):
        self.host, self.port, self.name = host, port, name
        self.conn = False
        self.last_message = ''
        self.text_to_send = 'this is a long test'

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

        self.outp(self.name)

        self.display_text = display_text

        self.input_thread = threading.Thread(target=self.inp, daemon=True)
        self.input_thread.start()
        #self.main()
    
    def outp(self, msg):
        self.conn.sendall(bytes(msg, 'UTF-8'))
    
    def inp(self):
        global is_running
        while is_running:
            self.last_message = self.conn.recv(2048).decode('UTF-8')
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


class MessagesBox(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.text = tk.Text(self, height=6, width=40)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.insert("end", 'Connected')
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

    def add_message(self, text):
        self.text.insert("end", ('\n' + text))
        self.text.see("end")

class App():
    def __init__(self) -> None:
        self.root =tk.Tk()
        OPTIONS = ["192.168.1.32", "localhost", "127.0.0.1"]
        variable = tk.StringVar(self.root)
        variable.set(OPTIONS[0]) # default value
        dropdown = tk.OptionMenu(self.root, variable, *OPTIONS)
        dropdown.pack()

        def ok():
            button.pack_forget()
            dropdown.pack_forget()
            self.start_client(variable.get()) # pass the IP adress

        button = tk.Button(self.root, text="OK", command=ok)
        button.pack()
        self.root.mainloop()

    def key_return_callback(self, event):
        self.client.outp(self.entry.get())
        self.entry.delete(0, tk.END)

    def start_client(self, ip):
        self.frame = MessagesBox(self.root)
        self.frame.pack(fill="both", expand=True)
        self.entry = tk.Entry()
        self.entry.bind('<Key-Return>', self.key_return_callback)
        self.entry.pack()
        self.client = Client(ip, self.frame.add_message)

app = App()