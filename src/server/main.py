from simplesocket import SimpleSocket
from args import args

server = SimpleSocket()

server.Players = [] # UUIDs [1, 2, 4, 7]
server.CurrentPlayer = None # UUID 4
server.MaxUUID = 0 # Biggest UUID 7
server.UUIDs = {} # Links client_socket to UUID

server.String = [] # String + UUID who made it

def ValidateAnswer(string):
    if string.count(" ") + string.count("_") > 0:
        return False
    for char in list("1234567890!\"\'£$%^&*()-=_+\{\}\\/@#~[]<>`¬|"):
        string.replace(char, "")
    return string

def GetKeyFromValue(dict, val):
    return list(dict.keys())[list(dict.values()).index(val)]

def NextPlayer():

    server.CurrentPlayer = server.Players[(server.Players.index(server.CurrentPlayer)+1) % len(server.Players)] # Who needs AI when you have me
    #client_socket = GetKeyFromValue(server.UUIDs, server.CurrentPlayer)
    print(f"Current Player: {server.CurrentPlayer}\nPlayers: {server.Players}")#\nCurrent socket: {client_socket}")
    server.all_clients({
        "next_string": server.CurrentPlayer
    })

def AddToString(string, uuid):
    server.String.append([string, uuid])
    server.all_clients({
        "new_string": server.String
    })
    NextPlayer()

def NewSocket(client_socket):
    server.UUIDs[client_socket] = server.MaxUUID + 1
    server.MaxUUID += 1
    server.Players.append(server.UUIDs[client_socket])
    server.all_clients({
        "players": server.Players
    })
    server.to_client(client_socket, {
        "new_string": server.String
    })
    if len(server.Players) == 1:
        server.CurrentPlayer = server.UUIDs[client_socket]

def SocketLeaving(client_socket):
    UUID = server.UUIDs[client_socket]
    if UUID and server.CurrentPlayer == UUID:
        NextPlayer()
    uuid = server.UUIDs[client_socket]
    server.Players.pop(server.Players.index(uuid))
    server.UUIDs[client_socket] = None
    print(uuid, "left")
    if len(server.Players) == 0:
        server.String = []
    else:
        server.all_clients({
            "players": server.Players
        })

def OnMessage(client_socket, data):
    UUID = server.UUIDs.get(client_socket)
    if not UUID: 
        print("NEW CONNECTION REGISTERED")
        NewSocket(client_socket)
    elif server.CurrentPlayer == UUID:
        if len(server.Players) < 2:
            server.all_clients({
                "message": "Not enough players",
                "error": True
            })
            return
        string = ValidateAnswer(data.get("string", "NONE"))
        if string: 
            AddToString(string, UUID)
        else:
            server.to_client(client_socket, {
                "message": "Not a valid word",
                "error": True
            }) 

#server.BindNewSocket(NewSocket) # commented because it would send the message before the gui is loaded lmao
server.BindReceive(OnMessage)
server.BindDisconnect(SocketLeaving)

server.init()