import pickle
import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import ttk

HOST = "127.0.0.1"
PORT = 9090


class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        self.gui_done = False
        self.running = True

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        gui_thread = threading.Thread(target=self.gui_loop)
        gui_thread.start()


    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.grid(row=0, column=1, padx=20, pady=1)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, width=30, height=20)
        self.text_area.grid(row=1, column=1, padx=20, pady=1)
        self.text_area.config(state="disable")
        self.text_area.tag_configure("info", foreground="blue")
        self.text_area.tag_configure("private", foreground="red")
        self.text_area.tag_configure("print", foreground="black")

        self.message_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.message_label.config(font=("Arial", 12))
        self.message_label.grid(row=0, column=0, padx=20, pady=1)

        self.input_area = tkinter.Text(self.win, width=30, height=20)
        self.input_area.grid(row=1, column=0)

        self.person = tkinter.StringVar(self.win)
        self.person.set('All')

        self.send_to = tkinter.OptionMenu(self.win, self.person, *['All'])
        self.send_to.config(width=30)
        self.send_to.grid(row=3, column=1, pady=3)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write, width=30)
        self.send_button.config(font=("Arial", 12))
        self.send_button.grid(row=3, column=0, padx=2, pady=3)

        self.gui_done = True
        self.win.title(self.nickname)

        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()


    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def init_online(self, message):
        for people in message['ask_online']:
            while not self.gui_done:
                pass
            if people != self.nickname:
                self.send_to['menu'].add_command(label=people, command=tkinter._setit(self.person, people))

    def write(self):
        message = self.input_area.get('1.0', 'end')
        send_to = self.person.get()
        obj = {
            'from': self.nickname,
            'send_to': send_to,
            'message': message,
        }
        data = pickle.dumps(obj)
        self.sock.sendall(data)
        self.input_area.delete('1.0', 'end')

    def receive(self):
        while self.running:
            try:
                message = pickle.loads(self.sock.recv(4096))
                if 'ask' in message:
                    self.sock.send(self.nickname.encode("utf-8"))
                elif 'ask_online' in message:
                    self.init_online(message)
                elif 'online' in message:
                    self.refresh_online(message)
                else:
                    if self.gui_done:
                        m = message['message']
                        tag = message['foreground']
                        self.text_area.config(state="normal")
                        self.text_area.insert('end', m, tag)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                print("Connection aborted")
                break
            except:
                print("Stopped")
                self.sock.close()
                break

    def refresh_online(self, online):
        if online['action'] == 'add':
            people = online['online']
            self.send_to['menu'].add_command(label=people, command=tkinter._setit(self.person, people))
        else:
            people = online['online']
            menu = self.send_to["menu"]
            index = menu.index(people)
            menu.delete(index)
            if self.person.get() == people:
                self.person.set('All')


client = Client(HOST, PORT)
