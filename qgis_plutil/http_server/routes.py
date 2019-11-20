# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from json import dumps

from flask import request

logger = logging.getLogger('plutil.http.s')


def define_common_routes(plugin, app, server):
    """ Some routes are always defined. """

    @app.route('/', methods=['GET', 'POST'])
    def route_index():
        logger.debug("Server reached on root path")

        the_args = request.args
        for arg in the_args:
            logger.debug("  - argument %s: %s", (arg, the_args[arg]))

        return dumps({
            'status': 'OK',
            'result': the_args
        })

    @app.route('/shut_me_down_used_for_restarts', methods=['POST'])
    def route_shutdown():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return dumps({
            'status': 'OK',
            'result': "Shutting down..."
        })

    @app.route('/result', methods=['GET', 'POST'])
    def route_result():
        logger.debug("We're being asked about a result")

        try:
            message_id = str(request.args['id'])
            with server.messages_lock:
                if message_id in server.messages:
                    logger.debug("message %r found in queue", message_id)
                    message = server.messages[message_id]
                    del server.messages[message_id]
                    result_type = message.result_type
                    result_data = message.result_data
                else:
                    logger.debug("message %r NOT found in queue", message_id)
                    result_type = 'NotFound'
                    result_data = 'Result may not be ready or it ' \
                                  'might have expired'
        except Exception:
            result_data = 'Exception in server while attempting to reply'
            result_type = 'Error'
            logger.error(result_data, exc_info=True)

        return dumps({
            'status': result_type,
            'result': result_data
        })
