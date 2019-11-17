# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from json import dumps

from flask import request

logger = logging.getLogger('plutil.http.s')


def define_common_routes(app, server, plugin):
    """ Some routes are always defined. """

    @app.route('/')
    def index():
        logger.debug("Server reached on root path")

        the_args = request.args
        for arg in the_args:
            logger.debug("  - argument %s: %s", (arg, the_args[arg]))

        return dumps({
            'status': 'OK',
            'result': the_args
        })

    @app.route('/shut_me_down_used_for_restarts', methods=['POST'])
    def shutdown():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return dumps({
            'status': 'OK',
            'result': "Shutting down..."
        })
