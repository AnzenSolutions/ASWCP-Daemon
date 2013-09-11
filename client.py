#!/usr/bin/env python

"""
Only import what we absolutely need first.
"""
from base64 import b64encode as encode,b64decode as decode
import sys
import os
import hashlib

# We want to use SHA-3 hashes but if we're not running Python >= 3.4, have to import the lib too
if sys.version_info < (3,4):
    import sha3

try:
    import json
except ImportError:
    import simplejson as json

import logging
from konf import Konf
from plugins.bases.registry import find_plugins, get_plugin_ref
import SocketServer as SS
from time import time
import hmac

log = logging.getLogger(__name__)

_BASE_DEFAULTS = {
    'arg_sep' : " ",
    "listen_port" : 5222,
    "tcp" : True,
    "threaded" : True,
    "sshport" : 22,
    "intf" : "eth0",

    # See _LOG_LEVELS to set
    "log_level" : "debug"
}

conf = Konf(defaults=_BASE_DEFAULTS)

NULL_RESP = {}

_LOG_LEVELS = {
    "error" : logging.ERROR,
    "critical" : logging.CRITICAL,
    "warning" : logging.WARNING,
    "info" : logging.INFO,
    "debug" : logging.DEBUG
}

loglevel = _LOG_LEVELS.get(str(conf.log_level).lower(), "info")

logging.basicConfig(level=loglevel, format='%(levelname)-8s at %(asctime)s : %(message)s')

plugins = find_plugins()

host,ip = plugins["cmd"]["init"]["ref"].init(conf=conf, socket=None).run()[1]

"""
ukey - Private key (unique key)
api_key - Key given from web panel
"""
ukey = None
api_key = None

# Where is our key data to be?
key_file = "%s/%s" % (os.path.expanduser("~"), ".aswcp.key")

hip = ""
ch = ""

try:
    hip,ch = str(sys.argv[1]).split(",")
except:
    pass

if hip == "" and ch == "" and os.path.exists(key_file):
    try:
        with open(key_file, "r") as fp:
            api_key, ukey = str(fp.read()).split(":")
    except:
        log.critical("No API key found in %s" % key_file)
else:
    import urllib2, httplib
    from urllib import urlencode

    logging.debug("Informing %s of challenge code: %s" % (hip, ch))
    data = urlencode({"challenge" : ch})
    req = urllib2.Request("%s/server/add" % hip, data)

    try:
        resp = urllib2.urlopen(req)
    except ValueError:
        log.critical("No host provided. Please pass <fqdn>:<challenge> to daemon to use.")
        sys.exit(1)
        
    kp = resp.read()
    try:
        api_key,ukey = str(kp).split(":")
    except:
        _,msg = kp.split("|")
        logging.critical(msg)
        sys.exit(1)

    logging.info("Recieved API key: %s" % api_key)
    logging.debug("Received API private key: %s" % ukey)
    
    ip = plugins["cmd"]["getip"]["ref"].init(conf=conf,socket=None).run()[1]
    
    data = urlencode({"info" : "OK|%s|4,%s" % (host,ip), "challenge" : ch})
    req = urllib2.Request("%s/server/done" % hip, data)
    resp = str(urllib2.urlopen(req).read())

    if resp[0] == "e":
        log.critical(resp[2:])
    else:
        log.info(resp[2:])
        with open(key_file,"w") as fp:
            fp.write(kp)

if ukey == None or api_key == None:
    sys.exit(1)

if ukey == "":
    logging.error("No private key found for system.  Please create one from the web panel and run %s -key <public api key>" % (sys.argv[0]))
    sys.exit(1)

call_start = 0
call_end = 0
prog_start = time()

def send_response(rid, api, status=True, data=""):
    tmp = {"status" : status, "data" : data}

    body = encode(json.dumps(tmp))

    enc = hashlib.sha3_512()
    enc.update(body)

    msg_sig = hashlib.sha3_512()
    msg_sig.update("%s%s%s" % (api, enc.hexdigest(), body))

    return "%s:%s:%s:%s" % (rid, api, msg_sig.hexdigest(), body)

class ASWCP_Daemon(SS.BaseRequestHandler):
    def handle(self):
        call_start = time()
        self.log = log
        self.data = self.request.recv(1024).strip()
        self.args = sys.argv
        self.prog_start = prog_start

        self.log.debug("Received from %s the following message: %s" % (self.client_address[0], self.data))

        if self.data == "":
            self.log.debug("Received no data from %s" % (self.client_address[0]))
            self.request.sendall(json.dumps(NULL_RESP))
            return None

        try:
            rid, api, sig, treq = self.data.split(":")

            self.log.debug("Request ID: %s ; API key: %s ; Message Signature: %s ; Encoded request: %s" % (rid, api, sig, treq))
            req = json.loads(decode(treq))

            msg_sig = hmac.new(ukey, treq, hashlib.sha512)
            
            if msg_sig.hexdigest() != sig:
                self.log.error("Message signatures did not match.")
                self.request.sendall(json.dumps({"status" : False, "data" : "Message signatures did not match."}))
                return None
            else:
                self.log.debug("Message signatures matched.")
        except:
            self.log.error("Missing data in request from server.")
            self.request.sendall(json.dumps({"status" : False, "data" : "Format: <request id>:<api key>:<message signature>:<JSON dump of {'cmd' : '', 'args' : ''}>"}))
            return None

        try:
            cmd = req['cmd']
        except KeyError:
            self.log.error("No command provided.")
            return None

        try:
            args = req['args']
        except KeyError:
            self.log.error("Missing 'args' request from server.")
            return None

        self.log.debug("Command requested: %s" % cmd)

        plugin = plugins["cmd"][cmd]['ref'].init(conf=conf, socket=self)
        
        status,data = plugin.run(*args)
        
        self.log.debug("Sending %s status response to server with data: \"%s\"" % (status, data))
        self.request.sendall(send_response(rid, api, status, data))

        call_end = time()

        self.log.debug("Request took %d seconds to complete." % (call_end - call_start))

if __name__ == "__main__":
    try:
        if conf.tcp:
            if conf.threaded:
                import threading
                class ThreadedTCPServer(SS.ThreadingMixIn, SS.TCPServer):
                    allow_reuse_address = True
                    daemon_threads = True

                    def __init__(self, addr, handler):
                        SS.TCPServer.__init__(self, addr, handler)

                server = ThreadedTCPServer((ip, conf.listen_port), ASWCP_Daemon)
            else:
                server = SS.TCPServer((ip, conf.listen_port), ASWCP_Daemon)
        else:
            if conf.threaded:
                import threading
                class ThreadedUDPServer(SS.ThreadingMixIn, SS.UDPServer):
                    allow_reuse_address = True
                    daemon_threads = True

                    def __init__(self, addr, handler):
                        SS.UDPServer.__init__(self, addr, handler)

                server = ThreadedUDPServer((ip, conf.listen_port), ASWCP_Daemon)
            else:
                server = SS.UDPServer((ip, conf.listen_port), ASWCP_Daemon)

        if conf.threaded:
            sthread = threading.Thread(target=server.serve_forever)
            #sthread.daemon = True
            sthread.start()
        else:
            try:
                server.serve_forever()
            except:
                pass
    except KeyboardInterrupt:
        pass

    #server.shutdown()
