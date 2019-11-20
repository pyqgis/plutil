# -*- coding: utf-8 -*-
"""
Contains the definition of the HttpServer class.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import threading
import time
from collections import OrderedDict

import requests
from PyQt5.QtCore import QThread

from ..thread_support.gui_side import GuiSide
from ..thread_support.thread_side import ThreadSide
from ..constants import UERROR, ADD_TO_QUEUE

logger = logging.getLogger('plutil.http.s')


class HttpServer(GuiSide):
    """

    """
    def __init__(self, plugin, routes_constructors=None):
        """
        Constructor.

        Arguments:
            plugin ():
                The plugin where we belong
            routes_constructors (list, None):
                The list of callables used for creating the routes
                before the server is started. see define_common_routes()
                for an example of such a callable.
        """
        super(HttpServer, self).__init__()
        self.plugin = plugin
        self.routes_constructors = routes_constructors \
            if routes_constructors else []

        self.server_thread = None
        self.app = None
        self.api = None
        self.prev_banner = None

        # These are processed messages that the thread wants to keep track
        # The gui side will process messages and keep them until
        # the thread takes them out or the list becomes full.
        self.messages = OrderedDict()
        self.messages_limit = 100
        self.messages_lock = threading.Lock()

    def __str__(self):
        """ Represent this object as a human-readable string. """
        return 'HttpServer()'

    def __repr__(self):
        """ Represent this object as a python constructor. """
        return 'HttpServer()'

    def message_accepted(self, message):
        """ We re-implement this so that we can add the message to queue. """
        if message.on_gui_side() == ADD_TO_QUEUE:
            with self.messages_lock:
                self.messages[str(message.message_id)] = message
                logger.debug("added message %r to http gui side queue",
                             message.message_id)
                while len(self.messages) > self.messages_limit:
                    logger.debug("dropping message %r because queue is full",
                                 message.message_id)
                    self.messages.popitem()

    def start(self, host=None, port=None):
        """
        Starts the http server.
        """
        logger.debug("flask server is being started...")
        try:
            from flask import cli
            from flask import Flask
            from flask_restful import Api
            from .routes import define_common_routes

            if host is None:
                host = self.plugin.get('http-server/host', '127.0.0.1')
            if port is None:
                port = int(self.plugin.get('http-server/port', 7768))

            def show_server_banner(env, debug, app_import_path, eager_loading):
                """ We need to monkey-patch this as it breaks the code. """
                pass
            self.prev_banner = cli.show_server_banner
            cli.show_server_banner = show_server_banner

            self.app = Flask('Flask-%s' % self.plugin.plugin_name)
            setattr(self.app, 'plutil_server', self)
            self.api = Api(self.app, catch_all_404s=True)

            # Register routes.
            define_common_routes(app=self.app, server=self, plugin=self.plugin)
            for func in self.routes_constructors:
                func(self.plugin, app=self.app, server=self)

            self.server_thread = ServerThread(
                host=host, port=port, app=self.app, server=self)
            self.tie(self.server_thread)
            self.server_thread.start()

            logger.info("server running at %s:%d", host, port)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            self.plugin.logger.log(UERROR, "Could not start http server",
                            exc_info=True)

    def stop(self, host=None, port=None):
        """
        Stops the http server.
        """
        logger.debug("flask server is being stopped...")

        try:
            if host is None:
                host = self.plugin.get('http-server/host', '127.0.0.1')
            if port is None:
                port = int(self.plugin.get('http-server/port', 7768))

            # Asking the server to shut down nicely.
            api_url = 'http://%s:%d/shut_me_down_used_for_restarts' % (host, port)
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'plutil',
                'Accept': 'application/json'
            }
            response = requests.post(api_url, headers=headers)

            # The server accepts or not.
            if response.status_code == 200:
                logger.debug("200 OK for request to shutdown")
                logger.debug(response.content)
                time.sleep(1)
            else:
                self.plugin.show_error(
                    self.plugin.tr("Unable to stop server (%r)") %
                    response.status_code)

            # Terminate the thread.
            self.server_thread.terminate()
            self.server_thread.wait()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            self.plugin.logger.log(UERROR, "Could not stop http server",
                                   exc_info=True)

        self.server_thread = None

        setattr(self.app, 'plutil_server', None)
        self.api = None
        self.app = None

        from flask import cli
        cli.show_server_banner = self.prev_banner

        logger.debug("flask server stopped")


class ServerThread(ThreadSide, threading.Thread):
    """ The object in the server thread. """
    def __init__(self, app, host, port, server):
        super(ServerThread, self).__init__(self)
        self.app = app
        self.host = host
        self.port = port
        self.plugin = server.plugin
        self.server = server

    def run(self):
        # noinspection PyBroadException
        try:
            self.thread_side_started()
            self.plugin.logger.debug(
                "Start serving at %r port %r",
                self.host, self.port)
            self.app.run(host=self.host, port=self.port, debug=True,
                         load_dotenv=True, use_evalex=False, use_reloader=False)
        except Exception as exc:
            self.plugin.logger.error("Failed to run the server", exc_info=True)
