from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import threading
import websockets
from websockets.sync.server import serve
import socket


IP = socket.gethostbyname(socket.gethostname())
PORT = 1337 # tuff
code = ""
clients = set()

def start_server():
    def handler(websocket):
        print(f"dis dum dum connected -> {websocket.remote_address}")
        clients.add(websocket)
        update_counter()
        try:
            while True:
                message = websocket.recv()
                print(f"sum dum dum sent dis: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("sum dum dum disconnected")
        except Exception as e:
            print(f"ugh client handler errored:\n{e}")
        finally:
            clients.remove(websocket)
            update_counter()


    server = serve(handler, IP, PORT)
    server.serve_forever()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

root = Tk()
default_font = font.nametofont("TkDefaultFont")
default_font.config(family="Consolas", size=14)

ICON_LOGO = PhotoImage(file="resources/icons/transmit.png")
ICON_PICK_FILE = PhotoImage(file="resources/icons/script_add.png")
ICON_EXECUTE = PhotoImage(file="resources/icons/play_green.png")
root.title("Netsploit")
root.geometry("350x225")
root.resizable(False, False)
root.iconphoto(True, ICON_LOGO)
status_label = ttk.Label(root, text=f"Listening @ {IP}", foreground="orange", font=(default_font["family"], default_font["size"], "bold"))
status_label.pack()
clients_label = ttk.Label(root, text=f"Clients connected: 0", foreground="gray")
clients_label.pack()

def update_counter():
    clients_label.configure(text=f"Clients connected: {len(clients)}")

def pick_file():
    global code
    global text
    global upload_btn

    file = filedialog.askopenfilename(filetypes=[
        ("All files", "*.*"),
        ("Text files", "*.txt"),
        ("Lua(u) files", ("*.lua", "*.luau"))
    ])

    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                code = ""
                while chunk := f.read(4096):
                    code += chunk
                text.delete(1.0, "end")
                text.insert("end", code)
        except UnicodeDecodeError:
            messagebox.showerror("Netsploit", "Invalid file encoding")
        except PermissionError:
            messagebox.showerror("Netsploit", "Permission denied")
        except FileNotFoundError:
            messagebox.showerror("Netsploit", "File not found")
        except Exception as e:
            messagebox.showerror("Netsploit", f"Failed to read file: {str(e)}")


def upload():
    global text
    global clients

    queued_code = text.get(1.0, "end")
    if queued_code == "" or queued_code == "\n":
        messagebox.showwarning("Netsploit", "No code to execute.")
        return
    if not clients:
        messagebox.showwarning("Netsploit", "No clients connected.")
        return
    try:
        for client in list(clients):
            try:
                client.send(queued_code)
            except Exception as c_e:
                print(f"ugh sending over code to a client failed:\n{c_e}")
        messagebox.showinfo("Netsploit", f"Code sent to {len(clients)} client(s).")
    except Exception as e:
        messagebox.showerror("Netsploit", f"Failed to send code:\n{e}")

text_container = ttk.Frame(root)
text_container.pack(anchor="center", fill="both", padx=10)
text_frame = ttk.Frame(text_container)
text_frame.pack(expand=True)
def tabs2spaces(event):
    text.insert("insert", "    ")
    return "break"
text = Text(text_frame, wrap="none", height=7, width=45)
text.bind("<Tab>", tabs2spaces)
v_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview)
h_scroll = ttk.Scrollbar(text_frame, orient="horizontal", command=text.xview)
text.grid(row=0, column=0, sticky=NSEW)
v_scroll.grid(row=0, column=1, sticky=NS)
h_scroll.grid(row=1, column=0, sticky=EW)
text_frame.grid_rowconfigure(0, weight=1)
text_frame.grid_columnconfigure(0, weight=1)
v_scroll.config(command=text.yview)

buttons = ttk.Frame()
buttons.pack(pady=1)
upload_btn = ttk.Button(buttons, text="Execute", command=upload, image=ICON_EXECUTE, compound="right")
upload_btn.grid(row=0, column=1, padx=5)
pick_file_btn = ttk.Button(buttons, text="Open", command=pick_file, image=ICON_PICK_FILE, compound="right")
pick_file_btn.grid(row=0, column=0, padx=5)


root.mainloop()