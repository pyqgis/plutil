# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

from flask import cli
from flask import Flask
from flask_restful import Api

import logging

logger = logging.getLogger('plutil.http.s')


def show_server_banner(env, debug, app_import_path, eager_loading):
    """ We need to monkey-patch this as it breaks the code. """
    pass


logger.debug("flask functionality created")
cli.show_server_banner = show_server_banner
app = Flask("SisCaRo")
api = Api(app, catch_all_404s=True)
