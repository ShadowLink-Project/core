from func import *

net_signature = genRandomStr(36)
f = open("./serverdata/.net_signature", "w")
f.write(net_signature)
f.close()