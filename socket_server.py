import socket
import sys
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 1234 if len(sys.argv) == 1 else int(sys.argv[1])
sock.bind(('localhost', port))
sock.listen(5)

def process(msg):
    #print("actual processing:" + msg)
    print(msg)

try:
    while True:
        conn, info = sock.accept()
        data = conn.recv(1024).decode("utf-8")
        print(type(data))
        while data:
            data = data.lstrip('\n')
            while(data.find('\n')>0):
                data = data.lstrip('\n')
                databuff = data.split('\n')[0]
                process(databuff)
                if data.find('\n'):
                    data = data[data.find('\n')+1:]
                    data = data.lstrip('\n')
                else:
                    break
            data += conn.recv(1024).decode("utf-8")
except KeyboardInterrupt:
    sock.close
print("all done")

