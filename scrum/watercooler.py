import logging
import signal
import time

from urllib.parse import urlparse
from django import shortcuts

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_command_line, options
from tornado.web import Application
from tornado.websocket import WebSocketHandler

define('debug', default=False, type=bool, help='Run in debug mode')
define('port', default=8080, type=int, help="Server port")
define('allowed_hosts', default="localhost:8080", multiple=True,
        help='Allowed hosts for cross domain connections')

class SprintHandler(WebSocketHandler):
    """Trata atualizações de tempo real no quadro de tarefas."""

    def check_origin(self, origin):
        allowed = super().check_origin(origin)
        parsed = urlparse(origin.lower())
        matched = any(parsed.netloc == host for host in options.allowed_hosts)
        return options.debug or allowed or matched

    def open(self, sprint):
        """Registra-se para receber atualizações de sprint em uma nova conexão."""

    def on_message(self, message):
        """Faz o broadcast das atualizações para outros clientes interessados."""

    def on_close(self):
        """Remove o registro."""

def shutdown(server):
    ioloop = IOLoop.instance()
    logging.info('Stopping server.')
    server.stop()

    def finalize():
        ioloop.stop()
        logging.info('Stopped.')
    
    ioloop.add_timeout(time.time() + 1.5, finalize)

if __name__ == "__main__":
    parse_command_line()
    application = Application([
        (r'/(?P<sprint>[0-9]+)', SprintHandler),
    ], debug=options.debug)
    server = HTTPServer(application)
    server.listen(options.port)
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown(server))
    logging.info('Starting server on localhost:{}'.format(options.port))
    IOLoop.instance().start()