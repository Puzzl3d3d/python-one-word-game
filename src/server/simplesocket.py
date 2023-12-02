import socket, threading, json, urllib.request
from args import args

hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)

class SimpleSocket:
    def __init__(self, *, ip=args.get("ip", server_ip) or server_ip, port=args.get("port", 1000), auto_convert=not args.get("no_auto_convert", False), debug=not args.get("no_debug", False)):
        self.server_socket = None

        self.clients = {}
        self.threads = []

        self.ip = ip
        self.port = port

        # Variables
        self.auto_convert = auto_convert

        if debug:
            self.print = print
        else:
            self.print = lambda *args: 0

    def init(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.bind((self.ip, self.port))

        self.server_socket.listen(1)

        self.print(f"Server listening on {self.ip}:{self.port}, connect with public ipv4 {self.get_public_ip()}")

        # Start listening for client connections
        self.make_thread(target=self._listen_for_clients, daemon=True).join()

    # Private methods
    def _new_socket_callback(self, client_socket):
        pass

    def _data_receive_callback(self, client_socket, data):
        self.print(self.clients[client_socket][0], "sent data:", data)
        self.all_clients(data, convert=True)
        pass

    def _disconnect_callback(self, client_socket):
        self.print(self.clients.get(client_socket, "Client"), "disconnected")

    def _start_receiving(self, client_socket):
        while True:
            try:
                if not self.clients.get(client_socket):
                    break
                data = client_socket.recv(1024 * 1024).decode()

                if data:

                    if self.auto_convert:
                        data = self.from_json(data)

                    if type(data) == list:
                        for data in data:
                            self._data_receive_callback(client_socket, data)
                    else:
                        self._data_receive_callback(client_socket, data)
            except ConnectionResetError:
                self._disconnect_callback(client_socket)
                self.clients.pop(client_socket)
                break

    def _listen_for_clients(self):
        while True:
            self.print("Waiting for client to connect")
            client_socket, client_address = self.server_socket.accept()
            self.print(f"Connected with {client_address[0]}:{client_address[1]}")
            self.clients[client_socket] = client_address
            self._new_socket_callback(client_socket)
            self.make_thread(target=self._start_receiving, daemon=True, args=(client_socket,))

    # Bind / Decorator functions
    def BindNewSocket(self, func):
        self._new_socket_callback = func

    def BindReceive(self, func):
        self._data_receive_callback = func

    def BindDisconnect(self, func):
        self._disconnect_callback = func

    # Public functions
    def from_json(self, json_string):
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

    def to_json(self, data):
        try:
            return json.dumps(data)
        except Exception as e:
            self.print("Exception in to_json :: Could not convert data:", data, "due to", e)

    def to_client(self, client_socket, data, convert=False):
        if convert or not isinstance(data, str):
            data = self.to_json(data)

        client_socket.send(data.encode())

    def all_clients(self, data, convert=False):
        if convert or not isinstance(data, str):
            data = self.to_json(data)

        for client_socket in self.clients.keys():
            try:
                if not client_socket or client_socket is None:
                    continue
                self.to_client(client_socket, data, convert=False)
            except Exception as e:
                print(f"Exception in all_clients :: {e}")
                pass

    def get_socket_from_address(self, client_address):
        try:
            return list(self.clients.keys())[list(self.clients.values()).index(client_address)]
        except Exception as e:
            self.print(f"Exception in get_socket_from_address :: {e}")
            return None

    def get_address_from_socket(self, client_socket):
        return self.clients.get(client_socket, None)

    def make_thread(self, *args, **kwargs):
        thread = threading.Thread(*args, **kwargs)
        self.threads.append(thread)
        thread.start()
        return thread

    @staticmethod
    def get_public_ip():
        external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

        return external_ip

if __name__ == "__main__":
    server = SimpleSocket()
    server.init()