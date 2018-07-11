# -*- coding: utf-8 -*-
""" Main App module """

import atexit
import logging
from flask import Flask
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.background import BackgroundScheduler

from currency_scraper import commands
from currency_scraper.admin import register_admin
from currency_scraper.config import DevConfig
from currency_scraper.extensions import migrate, db
from currency_scraper.tasks import ingest_latest_currency


def create_app(config_object=DevConfig):
    """An application factory
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_commands(app)
    register_admin(app)

    handler = RotatingFileHandler('currency_scraper.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(ingest_latest_currency, 'cron', minute='0', hour='9', day_of_week='1-5')
    sched.start()
    atexit.register(lambda: sched.shutdown(wait=False))

    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db, directory='currency_scraper/migrations')
    return None


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
