#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os
sys.path.append("../lib")
import params
from framedSock import framedSend, framedReceive

def init_client():
    global s, debug
    progname = "Client"
    switchesVarDefaults = (
        (('-s', '--server'), 'server', "127.0.0.1:50001"),
        (('-d', '--debug'), "debug", False),
        (('-?', '--usage'), "usage", False))
    paramMap = params.parseParams(switchesVarDefaults)
    server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

    if usage:
        params.usage()
    try:
        serverHost, serverPort = re.split(":", server)
        serverPort = int(serverPort)
    except:
        print("Can't parse server:port from '%s'" % server)
        sys.exit(1)

    s = None
    for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
            s = socket.socket(af, socktype, proto)
        except socket.error as msg:
            print(" error: %s" % msg)
            s = None
            continue
        try:
            print(" attempting to connect to %s" % repr(sa))
            s.connect(sa)
        except socket.error as msg:
            print(" error: %s" % msg)
            s.close()
            s = None
            continue
        break
    if s is None:
        print('could not open socket')
        sys.exit(1)

def send_message():
    while True:
        user_input = input("Enter Message\n> ")
        if re.match("put\s[\w\W]+", user_input):
            trash, file = user_input.split(" ",1)
            if os.path.exists("%s/%s" % (os.getcwd(), file)):
                msg = "put " + file.rsplit('/', 1)[-1]
                framedSend(s, msg.encode())
                framedSend(s, open(file, "rb").read(), 1)
            else:
                print("File Doesn't Exist.")
        elif re.match("get\s[\w\W]+", user_input):
            framedSend(s, user_input.encode())
            payload = framedReceive(s)
            if payload.decode() == "true":
                trash, file = user_input.split(" ",1)
                writer = open("%s/%s" % (os.getcwd(), file), "wb+")
                payload = framedReceive(s)
                writer.write(payload)
                writer.close()
                print("Transfer Done.")
            else:
                print("File not Found.")
        elif user_input == "quit":
            print("Killing Server...")
            framedSend(s, "quit".encode())
            print("Response:", framedReceive(s))
            sys.exit(0)
        else:
            framedSend(s, user_input.encode())
            print("Response:", framedReceive(s))

if __name__ == '__main__':
    init_client()
    try:
        send_message()
    except Exception as e:
        print("Server Disconnected. Trying Again.")
        send_message()