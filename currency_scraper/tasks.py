# -*- coding: utf-8 -*-
""" Tasks for scheduling """

from datetime import datetime
from flask import current_app as app

from currency_scraper.api_clients import FixerApiClient
from currency_scraper.models import BaseCurrency


def ingest_latest_currency():
    '''
    Retrieve and ingest the latest currency from fixer.io
    and check if database has at least one month of data

    :return: None
    '''

    today = datetime.today()

    fixer_client = FixerApiClient(
        host=app.config['FIXER_BASE_URL'],
        api_key=app.config['FIXER_API_KEY']
    )

    currency_data = fixer_client.get_rates()
    app.logger.info(f'Data retrieved {currency_data}')
    if not currency_data.error:
        BaseCurrency.imgest_daily_data(data=currency_data)

    missing_days = BaseCurrency.get_missing_working_days(day=today.date(), interval=31, base='EUR')
    for day in missing_days:
        currency_data = fixer_client.get_rates(date=day.strftime('%Y-%m-%d'))
        if not currency_data.error:
            BaseCurrency.imgest_daily_data(data=currency_data)
