import socket
from vendor.func import *
import cryptocode
from threading import Thread

net = {}

sock = socket.socket(socket.AF_INET)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", 1080))

net_signature = ""

if os.path.exists("serverdata/.net_signature"):
	net_signature = open("serverdata/.net_signature", "r").read()
else:
	print("No found the net signature!")
	exit()

sock.listen(40)
def listen_client(conn, addr):
    while True:
        print("Waiting for a command...")
        raw_data = conn.recv(1024)
        data = raw_data.decode("utf8").split("\00")

        if data[0] == "SERVER":
            # Exit
            if data[1] == "QUIT":
                print("\nConnection closed")
                conn.close()
                break
            elif data[1] == "NEWAUTH":
                objs = data[2].split(" ")
                h, p = addr
                conn.send(to_bytes(cryptocode.encrypt(f"{objs[0]};{objs[1]};{h}", net_signature)))
            elif data[1] == "SIGNUP":
                auth = cryptocode.decrypt(data[2], net_signature)
                if auth == False:
                	conn.send(to_bytes("Invalid login or password."))
                	continue
                objs = auth.split(";")
                # objs[0] - user
                # objs[1] - passwd
                # objs[2] - 000.000.000
                if not checkAcc(net, objs[0], objs[2]):
                    # append account in network
                    net[objs[0]] = (conn, objs[2])
                    conn.send(to_bytes("DONE"))
            elif data[1] == "CHAT":
                objs = data[2].split(" ")
                # objs[0] - user
                # objs[1] - withuser
                connect, ip = net[objs[1]]
                flush_mess(to_bytes(packed(f".{objs[1]}", "CHAT", objs[0])), connect)

        elif data[0][0] == ".":
            if data[1] == "TXTMSG":
                print(data)
                connect, ip = net[data[0].replace(".","")]
                flush_mess(to_bytes(packed(data[0], "TXTMSG", data[2])), connect)
                print(data[0], "TXTMSG", data[2])
            elif data[1] == "CHATCOM":
                connect, ip = net[data[0].replace(".", "")]
                flush_mess(to_bytes(packed(data[0], "CHATCOM", data[2])), connect)
        print("Received data ", end="")
        print(data)
        print()

while True:
    print('Waiting for a connection...')
    conn, addr = sock.accept()
    print("Connected!\n")
    t = Thread(target=listen_client, args=(conn,addr))
    t.daemon = True
    t.start()
