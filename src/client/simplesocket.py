import socket, threading, json
from args import args

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
    
if __name__ == "__main__":
    client = SimpleSocket(auto_convert=True)
    client.init()