#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2016 Megan Sumner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #uses regex to find the host name and port number
    def get_host_port(self,url):
        #from claesv at  http://stackoverflow.com/questions/9530950/parsing-hostname-and-port-from-string-or-url Sept. 26, 2016
        p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'

        m = re.search(p,url)
        host = m.group('host') 
        port = m.group('port') 
        if len(port) == 0:
            port = 80
        else:
            port = int(port)
        
        return host, port
 
    #connects to socket
    def connect(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return s
    
    #gets status code using regexes
    def get_code(self, data):
        p = '(HTTP\/1.[0-1] )(?P<code>\d\d\d)'
        m = re.search(p, data)
        code = m.group('code')
        return int(code)

    def get_headers(self,data):
        return len(str(data))

        #get body and headers by spliting data
    def get_body(self, data):
        #John Zwinck at http://stackoverflow.com/questions/599953/how-to-remove-the-left-part-of-a-string Sept. 27. 2016
        headers, body = data.split('\r\n\r\n', 1)
        return headers, body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""
        host, port = self.get_host_port(url)
        sock = self.connect(host, port)
        #parse url to get the parts of the url
        parse_result = urlparse(url)
        #if query is empty
        if parse_result[4] == None:
            sock.sendall("GET " + parse_result[2] + "HTTP/1.1\r\n")
        #if there is a query
        else:
            sock.sendall("GET "+ parse_result[2] + "?"  + parse_result[4] + " HTTP/1.1\r\n")
        sock.sendall("Host:" + host + "\r\n")
        sock.sendall("\r\n")
        data = self.recvall(sock)
        code = self.get_code(data)
        headers, body = self.get_body(data)
        sys.stdout.write(data)
        sock.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host, port = self.get_host_port(url)
        sock = self.connect(host, port)
        sock.sendall("POST / HTTP/1.1\r\n")
        sock.sendall("Host:" + host + "\r\n")
        sock.sendall("Content-Type: application/x-www-form-encoded, text/html\r\n")
        #if there is nothing to be POSTed
        if args == None:
            sock.sendall("Content-Length: 0\r\n\r\n")
        #encode the POST request and send its length
        else:
            args_encoded = urllib.urlencode(args, True)
            length = self.get_headers(args_encoded)
            sock.sendall("Content-Length: " + str(length) + "\r\n\r\n")
            sock.sendall(str(args_encoded))
        data = self.recvall(sock)
        code = self.get_code(data)
        headers, body = self.get_body(data)
        sys.stdout.write(data)
        sock.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
        
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )  
