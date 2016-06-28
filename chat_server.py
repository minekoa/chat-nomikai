from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi, sleep

import cgi
import wsgiref.util
import re
from chat_commander import ChatCommander
from chat_logger import ChatLogger

def wsgi_query(environ):
    wsgi_input     = environ['wsgi.input']
    content_length = int(environ.get('CONTENT_LENGTH'))
    return dict(cgi.parse_qsl(wsgi_input.read(content_length)))

def wsgi_scheme_and_netloc(environ):
    ''' "<scheme>://<netloc>/" -> ("<scheme>", "<netloc>") '''
    return tuple(wsgiref.util.application_uri(environ).strip('/').split('://'))

class User(object):
    def __init__(self, ws): self.websocket = ws
    def send(self, msg):    self.websocket.send(msg)
    def receive(self):      return self.websocket.receive()

class ChatApp(object):
    def __init__(self):
        self.listener_list   = set()
        self.commander = ChatCommander()
        self.commander.setMessageFunction(self.broadcast)
        self.listener_list.add(ChatLogger('backlog.txt'))

    def broadcast(self, msg):
        remove = set()
        for lsnr in self.listener_list:
            try:
                lsnr.send(msg)
            except Exception:
                remove.add(lsnr)
        for lsnr in remove:
            self.listener_list.remove(lsnr)

    def __call__(self, environ, start_response):  
        path    = environ["PATH_INFO"]
        method  = environ["REQUEST_METHOD"]

        if path == "/": 
            return self.index_handle(environ, start_response)
        elif path == "/client" and method == "POST":
            return self.client_handle(environ, start_response)
        elif path == "/chat":  
            return self.chat_handle(environ, start_response)
        elif re.match('/img/.*', path):
            return self.img_handle(environ, start_response, path)
        elif re.match('/js/.*', path):
            return self.js_handle(environ, start_response, path)
        elif re.match('/css/.*', path):
            return self.css_handle(environ, start_response, path)
        else:
            start_response("404 NOT FOUND", [("Content-Type", "text/plain")])  
            return "404 NOT FOUND ;-p"

    def index_handle(self, environ, start_response):
        uri = "%s://%s/client" % wsgi_scheme_and_netloc(environ)
        start_response("200 OK", [("Content-Type", "text/html;charset=UTF-8")])  
        return open('./chat_login.html').read() % uri

    def client_handle(self, environ, start_response):
        username = wsgi_query(environ)['name']
        uri      = "ws://%s/chat" % wsgi_scheme_and_netloc(environ)[1]
        start_response("200 OK", [("Content-Type", "text/html;charset=UTF-8")])  
        return open('./chat_client.html').read() % (uri, username)

    def chat_handle(self, environ, start_response):
        user = User(environ['wsgi.websocket'])
        self.listener_list.add(user)
        print 'enter!', len(self.listener_list)
        while 1:
            msg = user.receive()
            if msg is None: break
            if not '!ninja' in [i.strip() for i in msg.split(';')]:
                self.broadcast(msg)

            self.commander.run(msg)
        print 'exit!', len(self.listener_list)

    def img_handle(self, environ, start_response, path):
        start_response("200 OK", [("Content-Type", "image/jpeg")])
        return open(path[1:],'rb') # remove '/'

    def js_handle(self, environ, start_response, path):
        start_response("200 OK", [("Content-Type", "text/javascript")])
        return open(path[1:],'r') # remove '/'

    def css_handle(self, environ, start_response, path):
        start_response("200 OK", [("Content-Type", "text/css")])
        return open(path[1:],'r') # remove '/'
        
if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8080), ChatApp(), handler_class=WebSocketHandler)
    server.serve_forever()
