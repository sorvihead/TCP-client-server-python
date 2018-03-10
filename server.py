import asyncio


class ClientServerProtocol(asyncio.Protocol):
    storage = []

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        if 'put' not in str(data) and 'get' not in str(data):
            self.transport.write(b'error\nwrong command\n\n')
        else:
            if "put" in str(data):
                resp = self.process_data(data.decode())
                self.transport.write(resp.encode())
            if "get" in str(data):
                c = ''
                for i in self.get(data):
                    if i == '\n' or i == 'ok\n':
                        c+=i
                    else:
                        c+=str(i)+' '
                self.transport.write(c.encode()+b'\n')


    def get(self, line):
        lst = []
        if "*" in str(line):
            lst.append('ok\n')
            if len(self.storage)!=0:
                for i in self.storage:
                    for j in i.values():
                        for c in j:
                            lst.append(c)
            else:
                return "ok\n\n"
            return lst
        else:
            line = line.decode()
            line = line[4:-1]
            lst.append('ok\n')
            for i in self.storage:
                if line in i.keys():
                    for j in i[line]:
                        lst.append(j)
                else:
                    continue
            return lst


    def process_data(self,line):
        line = str(line)
        try:
            line = line[4:-1].split(' ')
        except Exception:
            return 'error\nwrong command\n\n'
        try:
            if {line[0]:[line[0],line[1],line[2],'\n']} not in self.storage:
                self.storage.append({line[0]:[line[0], line[1], line[2], '\n']})
        except Exception:
            return 'ok\n\n'
        return 'ok\n\n'

def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ClientServerProtocol,
        host, port
    )

    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == "__main__":
    run_server("127.0.0.1", 8888)