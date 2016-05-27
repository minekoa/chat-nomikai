from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi, sleep

import cgi
import wsgiref.util
from chat_commander import ChatCommander

def broadcast(msg):
    remove = set()
    for s in ws_list:
        try:
            s.send(msg)
        except Exception:
            remove.add(s)
    for s in remove:
        ws_list.remove(s)

ws_list   = set()
commander = ChatCommander()
commander.set_message_function(broadcast)

def chat_handle(environ, start_response):
    ws = environ['wsgi.websocket']
    ws_list.add(ws)
    print 'enter!', len(ws_list)
    while 1:
        msg = ws.receive()
        if msg is None: break

        broadcast(msg)
        commander.run(msg)
        for cmsg in commander.messages:
            broadcast(cmsg)

    print 'exit!', len(ws_list)

def wsgi_query(environ):
    wsgi_input     = environ['wsgi.input']
    content_length = int(environ.get('CONTENT_LENGTH'))
    return dict(cgi.parse_qsl(wsgi_input.read(content_length)))

def chatapp(environ, start_response):  
    path    = environ["PATH_INFO"]
    method  = environ["REQUEST_METHOD"]
    app_uri = wsgiref.util.application_uri(environ).strip('/').split('://')   # "<scheme>://<netloc>/" -> ["<scheme>", "<netloc>"]

    if path == "/": 
        start_response("200 OK", [("Content-Type", "text/html;charset=UTF-8")])  
        uri = "%s://%s/client" % (app_uri[0], app_uri[1])
        return open('./chat_login.html').read() % uri

    elif path == "/client" and method == "POST":
        query = wsgi_query(environ)
        username = query['name']
        start_response("200 OK", [("Content-Type", "text/html;charset=UTF-8")])  
        uri = "ws://%s/chat" % app_uri[1]
        return open('./chat_client.html').read() % (uri, username)

    elif path == "/chat":  
        return chat_handle(environ, start_response)

    else:
        start_response("404 NOT FOUND", [("Content-Type", "text/plain")])  
        return "404 NOT FOUND ;-p"

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8080), chatapp, handler_class=WebSocketHandler)
    server.serve_forever()
