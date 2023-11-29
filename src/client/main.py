from simplesocket import SimpleSocket
from args import args
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