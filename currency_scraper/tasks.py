import logging
from datetime import datetime
from flask import current_app

from currency_scraper.api_clients import FixerApiClient
from currency_scraper.models import BaseCurrency

logger = logging.getLogger(__name__)


def ingest_latest_currency():
    '''
    Retrieve and ingest the latest currency from fixer.io
    and check if database has at least one month of data

    :return: None
    '''
    today = datetime.today()
    fixer_client = FixerApiClient(
        host=current_app.config.FIXER_BASE_URL,
        api_key=current_app.config.FIXER_API_KEY
    )

    currency_data = fixer_client.get_rates()
    if not currency_data.error:
        BaseCurrency.imgest_daily_data(data=currency_data)

    missing_days = BaseCurrency.get_missing_working_days(today=today, interval=31)
    for day in missing_days:
        currency_data = fixer_client.get_rates(date=day)
        if not currency_data.error:
            BaseCurrency.imgest_daily_data(data=currency_data)


def heartbeat():
    print('Heartbeat')
    logger.debug('Heartbeat')
