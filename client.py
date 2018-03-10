import socket
import time


class ClientError(Exception):
    pass


class ClientSocketError(ClientError):
    pass


class ClientProtocolError(ClientError):
    pass


class Client:
    def __init__(self, host, port, timeout=None):
        """initialize variables and try to establish a connection"""
        self.host = host
        self.port = port
        self.timeout = timeout
        try:
            self.sock = socket.create_connection((self.host, self.port), self.timeout)
        except socket.error as err:
            raise ClientSocketError("error create connection", err)

    def put(self, name, nums, timestamp=str(int(time.time()))):
        """Form the request and send it to the server
        If we meet in the answer 'wrong' we raise an error
        """
        data = str("put {0} {1} {2}\n".format(name, str(nums), str(timestamp)))
        try:
            self.sock.sendall(data.encode('utf8'))
        except socket.error as err:
            raise ClientSocketError("error send data ", err)
        try:
            answer = self.sock.recv(1024)
        except socket.error:
            raise ClientError
        if "wrong" in str(answer):
            raise ClientProtocolError


    def get(self, key):
        """Form the request and send it to the server
        If we meet in the answer 'wrong' we raise an error
        else we pass control to the method to_dict
        """
        try:
            self.sock.sendall(str("get {0}\n".format(key)).encode("utf8"))
        except socket.error as err:
            raise ClientSocketError("error send data ", err)
        try:
            data = self.sock.recv(1024).decode("utf8")
        except socket.error:
            raise ClientError
        if "wrong" in str(data):
            raise ClientError
        else:
            return self.to_dict(data)

    def to_dict(self, line):
        """Having received the answer, we convert it into a dictionary,
        with values - lists sorted by timestamp tuples
        """
        if str(line) == 'ok\n\n':
            return {}
        else:
            line1 = str(line)[3:-2]
            line1 = line1.split('\n')
        storage = {}
        for i in range(len(line1)):
            inf = line1[i].split(' ')
            try:
                storage[inf[0]]
                storage[inf[0]].append(tuple((int(inf[2]), float(inf[1]))))
                storage[inf[0]].sort()
            except KeyError:
                storage.setdefault(inf[0], [])
                storage[inf[0]].append(tuple((int(inf[2]), float(inf[1]))))
                storage[inf[0]].sort()
        return storage

    def close(self):
        """close connection"""
        try:
            self.sock.close()
        except socket.error as err:
            raise ClientSocketError("error close connection", err)


def _main():
    # check work client
    client = Client("127.0.0.1", 8888, timeout=5)
    client.put("test", 0.5, timestamp=1)
    client.put("test", 2.0, timestamp=2)
    client.put("test", 0.5, timestamp=3)
    client.put("load", 3, timestamp=4)
    client.put("load", 4, timestamp =5)
    print(client.get("*"))
    print(client.get("load"))
    print(client.get("test"))

    client.close()


if __name__ == "__main__":
    _main()
