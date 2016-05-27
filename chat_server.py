from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi, sleep

import cgi
import wsgiref.util
from chat_commander import ChatCommander

def wsgi_query(environ):
    wsgi_input     = environ['wsgi.input']
    content_length = int(environ.get('CONTENT_LENGTH'))
    return dict(cgi.parse_qsl(wsgi_input.read(content_length)))

def wsgi_scheme_and_netloc(environ):
    ''' "<scheme>://<netloc>/" -> ["<scheme>", "<netloc>"] '''
    return wsgiref.util.application_uri(environ).strip('/').split('://')   

class ChatApp(object):
    def __init__(self):
        self.ws_list   = set()
        self.commander = ChatCommander()
        self.commander.set_message_function(self.broadcast)

    def broadcast(self, msg):
        remove = set()
        for ws in self.ws_list:
            try:
                ws.send(msg)
            except Exception:
                remove.add(ws)
        for ws in remove:
            self.ws_list.remove(ws)

    def __call__(self, environ, start_response):  
        path    = environ["PATH_INFO"]
        method  = environ["REQUEST_METHOD"]
     
        if path == "/": 
            return self.index_handle(environ, start_response)
        elif path == "/client" and method == "POST":
            return self.client_handle(environ, start_response)
        elif path == "/chat":  
            return self.chat_handle(environ, start_response)
     
        else:
            start_response("404 NOT FOUND", [("Content-Type", "text/plain")])  
            return "404 NOT FOUND ;-p"

    def index_handle(self, environ, start_response):
        start_response("200 OK", [("Content-Type", "text/html;charset=UTF-8")])  
        schme_netloc = wsgi_scheme_and_netloc(environ)
        uri = "%s://%s/client" % (schme_netloc[0], schme_netloc[1])
        return open('./chat_login.html').read() % uri

    def client_handle(self, environ, start_response):
        query = wsgi_query(environ)
        username = query['name']
        start_response("200 OK", [("Content-Type", "text/html;charset=UTF-8")])  
        uri = "ws://%s/chat" % wsgi_scheme_and_netloc(environ)[1]
        return open('./chat_client.html').read() % (uri, username)

    def chat_handle(self, environ, start_response):
        ws = environ['wsgi.websocket']
        self.ws_list.add(ws)
        print 'enter!', len(self.ws_list)
        while 1:
            msg = ws.receive()
            if msg is None: break
            self.broadcast(msg)
            self.commander.run(msg)
        print 'exit!', len(ws_list)

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8080), ChatApp(), handler_class=WebSocketHandler)
    server.serve_forever()
