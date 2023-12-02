import argparse

# Default values for named arguments and flags
default_values = {
    'ip': "", # Automatically tries the public ip if not given
    'port': 1000,
    'no_auto_convert': False,
    "no_debug": False
}

# Create the parser
parser = argparse.ArgumentParser(description='ARG Module')

# Dynamically add arguments based on the default values
for arg, default in default_values.items():
    if isinstance(default, bool):
        # It's a flag, use store_true action
        parser.add_argument(f'-{arg}', action='store_true', help=f'A flag argument for {arg}')
    else:
        # It's a named argument with a default value
        parser.add_argument(f'-{arg}', type=type(default), default=default, help=f'A named argument for {arg}')

# Parse the arguments
args = parser.parse_args()

# Update default values with any provided command-line arguments
args = {arg: getattr(args, arg) for arg in default_values}




# -- NEW FILE HEADER --


import socket, threading, json


hostname = socket.gethostname()
client_ip = socket.gethostbyname(hostname)

class SimpleSocket:
    def __init__(self, *args, ip=args.get("ip", client_ip) or client_ip, port=args.get("port", 1000), auto_convert=not args.get("no_auto_convert", False), debug=not args.get("no_debug", False)):
        self.ip = ip
        self.port = port

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Variables
        self.auto_convert = auto_convert

        self.threads = []

        if debug:
            self.print = print
        else:
            self.print = lambda *args: 0

    def init(self):
        # Connect to the server
        while True:
            try:
                self.client_socket.connect((self.ip, self.port))
                self.print('Connected to {}:{}'.format(self.ip, self.port))
                break
            except Exception as error:
                self.print(
                    f"Could not connect to server: {error} | This may be because the server hasn't started yet\nRetrying...")

        self.makeThread(target=self._onConnect, daemon=True)
        self.makeThread(target=self._startRecieving, daemon=True).join()

    def __message(self):
        import getpass

        data = input("Send message to server: ")

        json_data = {
            "message": data,
            "user": getpass.getuser()
        }

        self.toServer(json_data, convert=True)

    def _onConnect(self):
        # Example function
        self.__message()

    def _onDataRecieve(self, data):
        # Example function
        #self.print("Server sent data:", data)
        if data.get("message"):
            print(f"<{data.get('user', 'User')}> {data.get('message', '(empty message)')}")
            self.__message()

    def _startRecieving(self):
        while True:
            try:
                data = self.client_socket.recv(1024 * 1024).decode()

                if data:

                    if self.auto_convert:
                        data = self.fromJSON(data)

                    try:
                        if type(data) == list:
                            for data in data:
                                self._onDataRecieve(data)
                        else:
                            self._onDataRecieve(data)
                    except Exception as error:
                        self.print("Could not handle data recieved:", data, "|", error)
            except (ConnectionResetError, ConnectionAbortedError):
                self.print("Disconnected from server, retry connection")
                return

    # Bind / Decorator functions
    def bindConnect(self, func):
        self._onConnect = func

    def bindRecieve(self, func):
        self._onDataRecieve = func

    # Public functions
    def fromJSON(self, json_string):
        json_string = json_string.split("}{")

        if len(json_string) > 1:
            for i in range(0, len(json_string), 1):
                json_string[i] = "{" + json_string[i] + "}"
            json_string[0] = json_string[0][1:]
            json_string[-1] = json_string[-1][0:-1]

        data = []

        for json_string in json_string:
            try:
                data.append(json.loads(json_string))
            except json.decoder.JSONDecodeError:
                self.print("Could not convert JSON:", json_string)

        return data if len(data) > 1 else data[0]

    def toJSON(self, data):
        try:
            return json.dumps(data)
        except:
            self.print("Could not convert data:", data)

    def toServer(self, data, convert=False):
        if convert or not isinstance(data, str):
            data = self.toJSON(data)

        self.client_socket.send(data.encode())

    def getSocket(self):
        return self.client_socket

    def getServerIP(self):
        return self.ip

    def getServerPort(self):
        return self.port

    def makeThread(self, *args, **kwargs):
        thread = threading.Thread(*args, **kwargs)
        self.threads.append(thread)
        thread.start()
        return thread
    



# -- NEW FILE HEADER --




import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from random import shuffle

client = SimpleSocket()

currentPlayer = None
myUUID = None

def render():
    global story_display
    global input_box
    global player_list_frame
    global root

    root = tk.Tk()
    root.title("One-Word Story Game")
    root.configure(bg='black')

    player_list_frame = tk.Frame(root, bg='black')
    player_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

    story_display = scrolledtext.ScrolledText(root, state='disabled', wrap='word', height=10, bg='black', fg='white')
    story_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    input_box = tk.Entry(root, bg='black', fg='white', insertbackground='white')
    input_box.pack(padx=10, pady=10, fill=tk.X)
    input_box.focus()

    input_box.bind('<Return>', send_word)

def send_word(event=None):
    """Send the typed word to the server."""
    try:
        word = input_box.get().strip()#.split()[0]  # Take only the first word
        if word:
            client.toServer({
                "string": word
            })
            input_box.delete(0, tk.END)
    except:
        messagebox.showerror("Error", "Not a valid word")
        print("womp womp")

COLORS = [
    'red', 'green', 'blue', 'magenta', 'orange', 'purple', 'pink', 'cyan',
    'gold', 'chocolate', 'violet', 'tomato', 'salmon', 'plum', 'orchid',
    'burlywood', 'bisque', 'beige', 'yellow', 'turquoise', 'tan'
]

def update_story_display(string):
    """Updates the story display with colored text for each client."""
    story_display.config(state='normal')
    story_display.delete('1.0', tk.END)

    print("String:",string)

    for word, uuid in string:
        color = COLORS[uuid % len(COLORS)]
        story_display.tag_config(color, foreground=color)
        story_display.insert(tk.END, word + " ", color)

    story_display.yview(tk.END)
    story_display.config(state='disabled')

def update_player_list(player_info):
    for widget in player_list_frame.winfo_children():
        widget.destroy()

    print(player_info)
    for uuid in player_info:
        print(uuid, currentPlayer)
        color = COLORS[uuid % len(COLORS)]
        if uuid == currentPlayer:
            bg_color = 'gray'
        else:
            bg_color = 'black'

        player_label = tk.Label(player_list_frame, text=uuid, bg=bg_color, fg=color)
        player_label.pack()

players = []

def onMessage(data):
    global players

    if data.get("uuid"):
        global myUUID
        myUUID = data["uuid"]
    elif data.get("new_string"):
        #update_story_display(data["new_string"])
        root.after(0, update_story_display, data.get("new_string"))
        root.after(0, update_player_list, players)  # Schedule update in main loop
    elif data.get("next_string"):
        # its stringing time
        global currentPlayer
        currentPlayer = data.get("next_string")
        #root.after(0, update_story_display, data.get("next_string"))  # Schedule update in main loop
    elif data.get("players"):
        players = data["players"]
        root.after(0, update_player_list, players)  # Schedule update in main loop
    elif data.get("error"):
        messagebox.showerror('Error', data.get("message", "No information provided"))

def onConnect():
    render()

    client.toServer({
        "new_user": True
    }, convert=True)

    # start stupid tkinter
    root.mainloop()

    print("TKINTER CLOSED")

    client.getSocket().close() # stop connection to server

    quit()

client.bindConnect(onConnect)
client.bindRecieve(onMessage)

client.init()