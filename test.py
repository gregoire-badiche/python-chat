import tkinter as tk

def choose_s_c(root: tk.Tk, next, options: dict):

    def choose_serv():
        options.update({'type': 'server'})
        next(options)

    def choose_client():
        options.update({'type': 'client'})
        next(options)

    client = tk.Button(root, text='Client', command=choose_client)
    serv = tk.Button(root, text='Server', command=choose_serv)

    client.pack()
    serv.pack()

def choose_opt(root: tk.Tk, next, options: dict):
    if(options["type"] == 'client'):
        choose_c_opt(root, next, options)
    else:
        choose_s_opt(root, next, options)

def choose_c_opt(root: tk.Tk, next, options: dict):

    def ok():
        pwd = entry.get() if is_password.get() else False
        options.update({'ip': variable.get(), 'password': pwd})
        next(options)
    
    def change_pwd():
        if(is_password.get()):
            entry.config(state='normal')
        else:
            entry.config(state='disabled')

    OPTIONS = ["192.168.1.32", "localhost", "127.0.0.1"]

    is_password = tk.IntVar()

    variable = tk.StringVar(root)
    variable.set(OPTIONS[0]) # default value
    dropdown = tk.OptionMenu(root, variable, *OPTIONS)
    dropdown.pack()

    c = tk.Checkbutton(root, text = "Password", command=change_pwd, variable=is_password)
    c.pack()

    entry = tk.Entry(root, state='disabled')
    entry.pack()

    button = tk.Button(root, text="OK", command=ok)
    button.pack()

def choose_s_opt(root: tk.Tk, next, options: dict):
    next(options)
    
def final_view(root: tk.Tk, next, options: dict):
    print(options)
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
    
    def key_return_callback(event):
        frame.add_message(entry.get())
        entry.delete(0, tk.END)

    frame = MessagesBox(root)
    frame.pack(fill="both", expand=True)
    entry = tk.Entry(width=41)
    entry.bind('<Key-Return>', key_return_callback)
    entry.pack()


class views_loader():
    def __init__(self, *args) -> None:

        self.root = tk.Tk()
        self.i = 0
        self.f = list(args)

    def next(self, options):

        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.i += 1
        self.f[self.i](self.root, self.next, options)
        
        
    
    def add_view(self, f):
        self.f += [f]
        return self
    
    def __call__(self):
        self.start()
    
    def start(self):
        self.f[0](self.root, self.next, {})
        self.root.mainloop()


views = views_loader() \
    .add_view(choose_s_c) \
    .add_view(choose_opt) \
    .add_view(final_view) \
    ()