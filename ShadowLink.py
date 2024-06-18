import datetime
import socket
import os.path
from vendor.func import *
from sympy import *
from colorama import init, Fore
from colorama import Back
from colorama import Style
from Crypto.Cipher import DES
import cryptocode
import threading
from threading import Thread

init(autoreset=True)

server = ""
if os.path.exists(".server"):
	f = open(".server", "r")
	server = f.read()
	
cur_chat = None

if(not os.path.exists(".stamp") or open(".stamp", "r").read() == ""):
	f = open(".stamp", "w")
	stamp_key = genRandomStr(8) #[:8]
	f.write(stamp_key)
	f.close()
STAMP = open(".stamp", "rb").read()
if server != "":
	sock = socket.socket(socket.AF_INET)
	sock.connect((server, 1080))
des2 = DES.new(STAMP, DES.MODE_ECB)

acc_name = ""
withuser = None
new_chat = False
newchat_with = ""

def recive_data():
	while True:
		global new_chat, newchat_with, cur_chat
		raw_data = sock.recv(1024)
		data = raw_data.decode("utf8").split("\00")
		if data[0] == f".{acc_name}":
			if data[1] == "CHAT":
				newchat_with = data[2]
				dop = ("-" * len(newchat_with))
				print("\n----------------------------------------" + dop)
				print(f"| Do you want to create the chat with .{newchat_with}? |")
				print("----------------------------------------" + dop)
				yes_no = input("Y/N? ").upper() == "Y"
				if yes_no:
					cur_chat = newchat_with
				flush_mess(to_bytes(packed(f".{newchat_with}", "CHATCOM", f"{acc_name} {yes_no}")), sock)
			elif data[1] == "CHATCOM":
				objs = data[2].split(" ")
				cur_chat = objs[0]
				if objs[1] == "True":
					print(Fore.GREEN + f"\nThe chat with .{cur_chat} has been successfully created!")
				else:
					print(Fore.RED + f"\n.{cur_chat} refused to create a chat!")
			elif data[1] == "TXTMSG":
				mess = data[2].replace("/dtacc", f"{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
				print(mess)
			
def set_server(server_host):
	global server, sock
	server = server_host
	sock = socket.socket(socket.AF_INET)
	sock.connect((server, 1080))

while True:
	f_acc = input("ShadowLink ")
	if "$newauth" in f_acc:
		objs = f_acc.split(" ")
		# objs[0] - $newauth
		# objs[1] - user
		# objs[2] - password
		flush_mess(to_bytes(packed("SERVER", "NEWAUTH", f"{objs[1]} {objs[2]}")), sock)
		auth_file = cryptocode.encrypt(cryptocode.encrypt(sock.recv(1024).decode("utf8"), STAMP.decode("utf8")), objs[2])
		f2 = open(f"auth/{objs[1]}.auth", "w")
		f2.write(auth_file)
		f2.close()
	elif "$setserver" in f_acc:
		objs = f_acc.split(" ")
		# objs[0] - $setserver
		# objs[1] - server host and port
		set_server(objs[1])
	elif f_acc == "$saveserver":
		f = open(".server", "w")
		f.write(server)
		f.close()
	elif f_acc == "$rsconn":
		sock.close()
	elif f_acc[0] == ".":
		acc_name = f_acc.replace(".", "")
		print(Fore.YELLOW + f"Authentication of '{acc_name}' accaunt on the ShadowLink...")
		auth = cryptocode.decrypt(open(f"auth/{acc_name}.auth", "r").read(), input("password: "))
		if auth == False:
			print(Fore.RED + "Invalid login or password.")
			continue
		auth = cryptocode.decrypt(auth, STAMP.decode("utf8"))
		flush_mess(to_bytes(packed("SERVER", "SIGNUP", auth)), sock)
		server_answer = sock.recv(1024)
		if server_answer.decode("utf8") == "DONE":
			print(Fore.GREEN + f"Operation done.")
			break
		else:
			print(Fore.RED + server_answer.decode("utf8"))
	elif f_acc == "$quit":
		flush_mess(to_bytes(packed("SERVER", "QUIT", "")), sock)
		sock.close()
		break
ri = Thread(target=recive_data)
ri.start()
while True:
	inp = input(f"ShadowLink.{acc_name} ")
	if inp == "$chat":
		print("С кем создать чат?")
		withuser = input("Ник .")
		inf = f"{acc_name} {withuser}"
		flush_mess(to_bytes(packed("SERVER", "CHAT", inf)), sock)
		cur_chat = withuser
	if inp == "$txt":
		text = input("Message: ")
		text = f"{acc_name} | /dtacc\n" + text + "\n"
		flush_mess(to_bytes(packed(f".{cur_chat}", "TXTMSG", text)), sock)
	elif inp == "$setserver":
		objs = f_acc.split(" ")
		# objs[0] - $setserver
		# objs[1] - server host and port
		set_server(objs[1])
	elif inp == "$saveserver":
		f = open(".server", "w")
		f.write(server)
		f.close()
	elif inp == "$rsconn":
		sock.close()
	elif inp == "$quit":
		flush_mess(to_bytes(packed("SERVER", "QUIT", "")), sock)
		sock.close()
		break
sock.close()