import tkinter as tk
import json, socket, threading, time, atexit

is_running = True
FILE_PATH = 'server_list.json'

# --------------------------------------------------------------------------------------------- #

def get_ip() -> str:
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def get_serv_list() -> list:
    f = open(FILE_PATH, 'r')
    data = json.loads(f.read())
    f.close()
    arr = [data["servers"][x] for x in data["servers"].keys()]
    return arr

def get_name_list() -> list:
    return [i['name'] for i in get_serv_list()]

def get_name_dict() -> dict:
    return {data["name"]: data for data in get_serv_list()}

# --------------------------------------------------------------------------------------------- #

class Server():
    
    def __init__(self, name, password, discoverable, port, display_text, host='0.0.0.0'):

        self.ip = get_ip()

        if(discoverable):
            self.register_handler = RegisterHandler(name, self.ip, port, bool(password))

        self.host, self.port, self.name = host, port, name
        self.display_text = display_text
        self.password = password
        self.conns_list = []
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((self.host, self.port))
        self.conn.listen()

        atexit.register(lambda: self.send_to_all('error', 'ServerClosed'))

        self.key = ''

        self.new_conn_thread = threading.Thread(target=self.accept_new_conn, daemon=True)
        self.new_conn_thread.start()

        self.main_thread = threading.Thread(target=self.main, daemon=True)
        self.main_thread.start()

        self.display_text('connected')
    
    def accept_new_conn(self):
        global is_running
        while is_running:
            client_socket, adrr = self.conn.accept()
            self.conns_list.append(ClientConnection(client_socket, adrr, self.password, self.send_to_all))
    
    def outp(self, kind, msg):
        self.send_to_all(kind, self.name + ' : ' + msg)

    def send_to_all(self, kind, msg):
        self.del_closed_conns()
        if(kind == 'message' or kind == 'info'):
            self.display_text(msg)
        for conn in self.conns_list:
            conn.outp(kind, msg)
    
    def del_closed_conns(self):
        to_del = []
        names = []
        for i in range(len(self.conns_list)):
            try:
                self.conns_list[i].outp('ping', '')
            except:
                to_del.append(i)
                if(self.conns_list[i].authentificated == True):
                    names.append(self.conns_list[i].name)
        for i in to_del[::-1]:
            self.conns_list.pop(i)
        for i in names:
            self.send_to_all('info', i + ' has disconnected')
    
    def main(self):
        global is_running
        while is_running:
            try:
                time.sleep(1)
                self.del_closed_conns()

            except KeyboardInterrupt:
                is_running = False

class ClientConnection():
    def __init__(self, conn, adrr, password, send_to_all):
        self.conn = conn
        self.adrr = adrr

        self.authentificated = True # used to check if the conn has passed the authentification

        self.send_to_all = send_to_all

        msg_len = int(self.conn.recv(2).decode('UTF-8'))
        self.last_message = self.conn.recv(msg_len).decode('UTF-8')

        try:
            self.credentials = json.loads(self.last_message)
            self.name = self.credentials['name']
            if(self.credentials['password'] != password):
                self.outp('error', 'Wrong password')
                raise Exception('WrongPassword')
        except:
            self.conn.close()
            self.authentificated = False
            return

        self.send_to_all('info', self.name + ' has connected')
        self.outp('info', 'Connected')

        self.inp_thread = threading.Thread(target=self.inp)
        self.inp_thread.start()

        self.last_message = ''

    def inp(self):
        global is_running
        c = True # c stands for continue
        while is_running and c:
            try:
                msg_len = int(self.conn.recv(2).decode('UTF-8'))
                self.last_message = self.conn.recv(msg_len).decode('UTF-8')
                self.last_message = json.loads(self.last_message)
                if(self.last_message['type'] == 'message'):
                    self.send_to_all('message', self.name + ' : ' + self.last_message['data'])
            except:
                self.conn.close()
                break
            if not self.last_message:
                c = False
                break

    def outp(self, type, data):
        if data:
            message = json.dumps({'type': type, 'data': data})
        else:
            message = json.dumps({'type': type})
        if(len(message) > 99):
            return
        msglength = str(len(message)) if len(message) > 9 else ('0' + str(len(message)))
        self.conn.sendall(bytes(msglength, 'UTF-8'))
        self.conn.sendall(bytes(message, 'UTF-8'))

class RegisterHandler():
    def __init__(self, name, ip, port, is_pw) -> None:
        self.file_path = FILE_PATH
        self.register(name, ip, port, is_pw)
        atexit.register(self.unregister)
    
    def register(self, name, ip, port, is_pw) -> None:
        f = open(self.file_path, "r")
        data = json.loads(f.read())
        f.close()
        f = open(self.file_path, "w")
        self.id = data["nextID"]
        data["servers"][self.id] = {'name': name, 'ip': ip, 'port': port, 'is_password': is_pw, 'id': self.id}
        data["nextID"] = str(int(self.id) + 1)
        f.write(json.dumps(data))
        f.close()

    def unregister(self) -> None:
        f = open(self.file_path, "r")
        data = json.loads(f.read())
        f.close()
        f = open(self.file_path, "w")
        del(data['servers'][self.id])
        f.write(json.dumps(data))
        f.close()

# --------------------------------------------------------------------------------------------- #

class Client():
    def __init__(self, host, name, password, port, display_text):
        self.host, self.port, self.name = host, port, name

        self.password = password

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

        self.last_message = {}

        credentials = {'name': self.name, 'password': self.password}

        self.outp('credentials', credentials)

        self.display_text = display_text

        self.input_thread = threading.Thread(target=self.inp, daemon=True)
        self.input_thread.start()
        # self.main()
    
    def outp(self, kind, data):
        global is_running
        if(not is_running):
            return
        if(type(data) is dict):
            message = {'type': kind}
            message.update(data)
            message = json.dumps(message)
        else:
            if data:
                message = json.dumps({'type': kind, 'data': data})
            else:
                message = json.dumps({'type': kind})
        if(len(message) > 99):
            return
        msglength = str(len(message)) if len(message) > 9 else ('0' + str(len(message)))
        self.conn.sendall(bytes(msglength, 'UTF-8'))
        self.conn.sendall(bytes(message, 'UTF-8'))
    
    def inp(self):
        global is_running
        while is_running:
            try:
                msg_len = int(self.conn.recv(2).decode('UTF-8'))
            except ValueError:
                self.conn.close()
                break
            self.last_message = self.conn.recv(msg_len).decode('UTF-8')
            self.last_message = json.loads(self.last_message)
            if self.last_message["type"] == 'ping':
                pass
            elif self.last_message["type"] == 'message' or self.last_message["type"] == 'info':
                self.display_text(self.last_message['data'])
            elif self.last_message["type"] == 'error':
                self.display_text('error : ' + self.last_message['data'])
        is_running = False
        self.display_text('disconnected')
    
    def main(self):
        global is_running
        while is_running:
            try:
                time.sleep(6)
                self.outp('message', 'hello !')
            except KeyboardInterrupt:
                is_running = False

# --------------------------------------------------------------------------------------------- #

def main():
    def choose_s_c(root: tk.Tk, options: dict):

        def choose_serv():
            options.update({'type': 'server'})
            for widget in root.winfo_children():
                widget.destroy()
            choose_opt(root, options)

        def choose_client():
            for widget in root.winfo_children():
                widget.destroy()
            options.update({'type': 'client'})
            choose_opt(root, options)

        client = tk.Button(root, text='Client', command=choose_client)
        serv = tk.Button(root, text='Server', command=choose_serv)

        client.pack()
        serv.pack()

    def choose_opt(root: tk.Tk, options: dict):
        if(options["type"] == 'client'):
            choose_c_opt(root, options)
        else:
            choose_s_opt(root, options)

    def choose_name(root: tk.Tk, options: dict) -> None:
        def next():
            if(x.get() != ''):
                options.update({'name': x.get()})
                for widget in root.winfo_children():
                    widget.destroy()
                final_view(root, options)
        tk.Label(root, text='What is your name ?', padx=5, pady=5).pack()
        x = tk.Entry(root)
        x.pack(padx=5, pady=5)
        tk.Button(root, text='Ok', command=next).pack(padx=5, pady=5)

    def choose_c_opt(root: tk.Tk, options: dict) -> None:

        def ok():
            if(ip_entry.get() and port_entry.get()):
                pwd = password_entry.get() if is_password.get() else False
                options.update({'ip': VALUES[variable.get()]['ip'], 'password': pwd, 'port': int(port_entry.get())})
                for widget in root.winfo_children():
                    widget.destroy()
                choose_name(root, options)
        
        def change_values(*args):
            new_values = VALUES[variable.get()]
            ip_entry.delete(0, tk.END)
            ip_entry.insert(tk.END, new_values["ip"])

            port_entry.delete(0, tk.END)
            port_entry.insert(tk.END, new_values["port"])

            is_password.set(new_values["is_password"])

            change_pwd()
        
        def change_pwd():
            if(is_password.get()):
                password_entry.config(state='normal')
            else:
                password_entry.config(state='disabled')

        FALLBACK_MSG = 'Custom server' # No server available
        CHOOSE_MSG = 'Custom server'
        OPTIONS = [CHOOSE_MSG] + get_name_list() if bool(get_name_list()) else [FALLBACK_MSG]
        if(bool(get_name_list())):
            VALUES = get_name_dict()
            VALUES.update({CHOOSE_MSG: {"name": "", "ip": "", "port": 8081, "is_password": False}})
        else:
            VALUES = {FALLBACK_MSG: {"name": "", "ip": "", "port": 8081, "is_password": False}}

        is_password = tk.IntVar()

        variable = tk.StringVar(root)
        variable.set(OPTIONS[0]) # default value
        variable.trace('w', change_values)

        tk.Label(root, text='Choose your server', padx=10, pady=10, font=('Arial', 15)).pack()

        tk.Label(root, text='Server list').pack()
        dropdown = tk.OptionMenu(root, variable, *OPTIONS)
        dropdown.pack()

        tk.Label(root, text = "IP").pack()
        ip_entry = tk.Entry(root)
        ip_entry.pack()

        tk.Label(root, text = "Port").pack()
        port_entry = tk.Entry(root)
        port_entry.pack()

        password_check = tk.Checkbutton(root, text = "Password", command=change_pwd, variable=is_password)
        password_check.pack()

        password_entry = tk.Entry(root, state='disabled')
        password_entry.pack()

        ok_btn = tk.Button(root, text="OK", command=ok)
        ok_btn.pack()

        change_values()

    def choose_s_opt(root: tk.Tk, options: dict):
        def ok():
            port = port_entry.get() if port_entry.get() else 8081
            discoverable = is_discoverable.get()
            pwd = password_entry.get() if is_password.get() else False
            options.update({'port': int(port), 'discoverable': discoverable, 'password': pwd})
            for widget in root.winfo_children():
                widget.destroy()
            choose_name(root, options)
        
        def change_pwd():
            if(is_password.get()):
                password_entry.config(state='normal')
            else:
                password_entry.config(state='disabled')
        

        is_discoverable = tk.IntVar(value=1)
        is_password = tk.IntVar()

        tk.Label(root, text='Server Options', padx=10, pady=10, font=('Arial', 15)).pack()

        password_check = tk.Checkbutton(root, text = "Include password", command=change_pwd, variable=is_password)
        password_check.pack()
        password_entry = tk.Entry(root, state='disabled')
        password_entry.pack()

        tk.Label(root, text='port').pack()
        port_entry = tk.Entry(root)
        port_entry.pack()
        port_entry.insert(tk.END, '8081')

        discoverable_check = tk.Checkbutton(root, text = "Make the server appears\non the server list", variable=is_discoverable)
        discoverable_check.pack()

        ok_btn = tk.Button(root, text="OK", command=ok)
        ok_btn.pack()
        
    def final_view(root: tk.Tk, options: dict):
        class MessagesBox(tk.Frame):
            def __init__(self, *args, **kwargs):
                tk.Frame.__init__(self, *args, **kwargs)

                self.text = tk.Text(self, height=6, width=40)
                self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
                self.text.configure(yscrollcommand=self.vsb.set)
                self.vsb.pack(side="right", fill="y")
                self.text.pack(side="left", fill="both", expand=True)
                self.text.insert("end", 'connection in process...')

            def add_message(self, text):
                self.text.insert("end", ('\n' + text))
                self.text.see("end")
        
        def key_return_callback(event):
            conn.outp('message', entry.get())
            entry.delete(0, tk.END)
        
        frame = MessagesBox(root)

        conn = Server(options['name'], options['password'], options['discoverable'], options['port'], frame.add_message) \
            if options["type"] == "server" else \
            Client(options['ip'], options['name'], options['password'], options['port'], frame.add_message)

        frame.pack(fill="both", expand=True)
        entry = tk.Entry(width=41)
        entry.bind('<Key-Return>', key_return_callback)
        entry.pack()

    root = tk.Tk()

    choose_s_c(root, {})
    root.mainloop()

if __name__ == "__main__":
    main()