#!/usr/bin/env python

import socket
import sys
import json
from base64 import b64encode as encode,b64decode as decode
import hashlib

if sys.version_info < (3,4):
	import sha3

data = " ".join(sys.argv[1:])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def make_request(req):
	tmp = req.split(" ")
	cmd = tmp[0]
	args = []

	enc = hashlib.sha3_512()
	enc.update("key")

	try:
		args = tmp[1:]
	except:
		pass

	body = encode("%s" % (json.dumps({"cmd" : cmd, "args" : args})))
	
	msg_sig = hashlib.sha3_512()
	msg_sig.update("%s%s%s" % ("key", enc.hexdigest(), body)) # public key, private key, data

	return "id:key:%s:%s" % (msg_sig.hexdigest(), body)

try:
	enc = hashlib.sha3_512()
	enc.update("key")
	h = hashlib.sha3_512()
	h.update("password")
	print h.hexdigest()
	
	sock.connect(("localhost", 5222))
	sock.sendall(make_request(data) + "\n")
	dat = str(sock.recv(1024))
	rid,api,sig,resp = dat.split(":")
	d = json.loads(decode(resp))
	print "> dat:",dat
	print "> rid:",rid,"api:",api,"resp:",d,",status",d['status'],",data:",d['data']

finally:
	sock.close()