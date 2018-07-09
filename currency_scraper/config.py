import os

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

APP_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = APP_DIR


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY', '(xY3UBSOB*{~=$7[#TnG(bo$=*M5Wm')

    PROJECT_ROOT = PROJECT_ROOT
    DEBUG = os.environ.get('DEBUG', False)

    DB_NAME = 'currency_scraper.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI', f'sqlite:///{os.path.join(PROJECT_ROOT, DB_NAME)}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FIXER_BASE_URL = 'http://data.fixer.io/api/'
    FIXER_API_KEY = 'df37fcab3df778798f1512099cd88eef'

    JOBS = [
        {
            'id': 'latest_currency_ingestion',
            'func': 'currency_scraper.tasks:ingest_latest_currency',
            'trigger': {
                'type': 'cron',
                'hour': 9,
                'minute': 0,
                'day': '*',
                'week': '*',
                'day_of_week': '1-5',
            }
        },
        # {
        #     'id': 'heartbeat',
        #     'func': 'currency_scraper.tasks:heartbeat',
        #     'trigger': {
        #         'type': 'interval',
        #         'seconds': 5,
        #     }
        # }
    ]

    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }

    SCHEDULER_EXECUTORS = {
        'default': {
            'max_workers': 2,
            'type': 'threadpool',
        },
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 1
    }


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = False
    DB_NAME = 'currency_scraper_dev.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI', f'sqlite:///{os.path.join(Config.PROJECT_ROOT, DB_NAME)}'
    )


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = False
    DB_NAME = 'currency_scraper_test.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI', f'sqlite:///{os.path.join(Config.PROJECT_ROOT, DB_NAME)}'
    )
