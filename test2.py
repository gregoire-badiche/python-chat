import tkinter as tk

class MessagesBox(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.text = tk.Text(self, height=6, width=40)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.insert('Connected')
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

    def add_message(self, entry):
        self.text.insert("end", ('\n' + entry.get()))
        entry.delete(0, tk.END)
        self.text.see("end")


if __name__ == "__main__":
    root =tk.Tk()
    frame = MessagesBox(root)
    frame.pack(fill="both", expand=True)
    entry = tk.Entry()
    entry.bind('<Key-Return>', lambda x: frame.add_message(entry))
    entry.pack()
    root.mainloop()