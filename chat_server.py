import os
import random
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi, sleep

import cgi

ws_list = set()

def chat_handle(environ, start_response):
    global cnt
    ws = environ['wsgi.websocket']
    ws_list.add(ws)
    print 'enter!', len(ws_list)
    while 1:
        msg = ws.receive()
        if msg is None:
            break
        remove = set()
        for s in ws_list:
            try:
                s.send(msg)
            except Exception:
                remove.add(s)
        for s in remove:
            ws_list.remove(s)
    print 'exit!', len(ws_list)

def chatapp(environ, start_response):  
    path = environ["PATH_INFO"]
    method = environ["REQUEST_METHOD"]

    print path

    if path == "/": 
        start_response("200 OK", [("Content-Type", "text/html;charset=UTF-8")])  
        return open('./chat_login.html').read() % "http://127.0.0.1:8080/client"

    elif path == "/client" and method == "POST":
        wsgi_input     = environ['wsgi.input']
        content_length = int(environ.get('CONTENT_LENGTH'))
        query = cgi.parse_qsl(wsgi_input.read(content_length))
        username = query[0][1]
        start_response("200 OK", [("Content-Type", "text/html;charset=UTF-8")])  
        return open('./chat_client.html').read() % ("ws://127.0.0.1:8080/chat", username)

    elif path == "/chat":  
        return chat_handle(environ, start_response)

    else:
        start_response("404 NOT FOUND", [("Content-Type", "text/plain")])  
        return "404 NOT FOUND ;-p"

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8080), chatapp, handler_class=WebSocketHandler)
    server.serve_forever()
