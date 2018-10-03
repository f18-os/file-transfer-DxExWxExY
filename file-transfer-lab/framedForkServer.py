#! /usr/bin/env python3
import sys, os, socket, re
sys.path.append("../lib")       # for params
import params
from framedSock import framedSend, framedReceive

def init_server():
    global sock, debug, addr, lsock
    switchesVarDefaults = (
        (('-l', '--listenPort') ,'listenPort', 50001),
        (('-d', '--debug'), "debug", False), # boolean (set if present)
        (('-?', '--usage'), "usage", False), # boolean (set if present)
        )

    progname = "echoserver"
    paramMap = params.parseParams(switchesVarDefaults)

    debug, listenPort = paramMap['debug'], paramMap['listenPort']

    if paramMap['usage']:
        params.usage()

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
    bindAddr = ("127.0.0.1", listenPort)
    lsock.bind(bindAddr)
    lsock.listen(5)
    print("listening on:", bindAddr)
    if not os.path.exists("%s/server_files" % os.getcwd()):
        os.makedirs("server_files")
        print("Created server_files Directory.")

if __name__ == '__main__':
    init_server()
    while True:
        sock, addr = lsock.accept()
        if not os.fork():
            print("new child process handling connection from", addr)
            payload = framedReceive(sock)
            print("Received: ", payload.decode())
            if re.match("put\s[\w\W]+", payload.decode()):
                trash, file = payload.decode().split(" ",1)
                writer = open("%s/server_files/%s" % (os.getcwd(), file), "wb+")
                framedSend(sock, "start".encode())
                payload = framedReceive(sock,1)
                writer.write(payload)
                writer.close()
                print("Transfer Done.")
            elif re.match("get\s[\w\W]+", payload.decode()):
                trash, file = payload.decode().split(" ",1)
                if os.path.exists("%s/server_files/%s" % (os.getcwd(),file)):
                    framedSend(sock,"true".encode())
                    framedSend(sock, open("%s/server_files/%s" % (os.getcwd(),file), "rb").read(), 1)
                    print("Transfer Done.")
                else:
                    framedSend(sock,"false".encode())
            elif payload == "quit".encode():
                framedSend(sock, "Server Killed.".encode(), debug)
                print("Exiting...")
                sys.exit(0)
            else:
                framedSend(sock, "Received".encode(), debug)