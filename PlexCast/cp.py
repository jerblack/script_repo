__author__ = 'Jeremy'
import cherrypy as cp
import os, socket, json

current_dir = os.path.dirname(os.path.abspath(__file__))
ip = socket.gethostbyname(socket.gethostname())
port = 84


class Root:
    @cp.expose
    def tx(self):
        print("Loading page", "'/css'")
        return "css here"


class StartCherryPy:
    def __init__(self):
        cp.config.update(
            {
                'server.socket_host': ip,
                'server.socket_port': port,
                'log.error_file': 'PlexCast.log',
                'log.screen': True,
            })
        conf = {
            '/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(current_dir, 'web'),
                'tools.staticdir.index': "default.htm"
        }}
        cp.quickstart(Root(), '/', config=conf)


if __name__ == '__main__':
    StartCherryPy()
