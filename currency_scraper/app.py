from flask import Flask
from currency_scraper import commands
from currency_scraper.admin import register_admin
from currency_scraper.config import DevConfig
from currency_scraper.extensions import migrate, db, scheduler


def create_app(config_object=DevConfig):
    """An application factory
    :param config_object: The configuration object to use.
    """

    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_commands(app)
    register_admin(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    scheduler.init_app(app)
    return None


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)


if __name__ == '__main__':
    app = create_app(DevConfig)
    scheduler.start()
    app.run()
