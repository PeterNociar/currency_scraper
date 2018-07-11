# -*- coding: utf-8 -*-
""" Test Models """

import pytest
import datetime

from currency_scraper.models import BaseCurrency, CurrencyRate


@pytest.mark.usefixtures('db')
class TestModels:
    response_json = {
        'success': True,
        'timestamp': 1531076648,
        'base': 'EUR',
        'date': '2018-07-08',
        'rates': {
            'AED': 4.31778,
            'AFN': 85.17518,
            'ALL': 126.616521,
        },
    }

    def test_imgest_daily_data_success(self):

        BaseCurrency.imgest_daily_data(data=self.response_json)

        base_currencies = list(BaseCurrency.query.all())

        assert len(base_currencies) == 1
        assert base_currencies[0].currency == self.response_json['base']
        assert base_currencies[0].date.isoformat() == self.response_json['date']

        currency_rates = list(CurrencyRate.query.all())
        assert len(currency_rates) == 3
        for rate in currency_rates:
            assert float(rate.rate) == self.response_json['rates'][rate.currency]

    def test_imgest_daily_data_duplicate_error(self):
        BaseCurrency.imgest_daily_data(data=self.response_json)
        BaseCurrency.imgest_daily_data(data=self.response_json)

        currency_rates = list(CurrencyRate.query.all())

        assert len(currency_rates) == 3
        for rate in currency_rates:
            assert float(rate.rate) == self.response_json['rates'][rate.currency]

    def test_get_working_days(self):
        day = datetime.date(2018, 1, 31)
        gen = BaseCurrency._get_working_days(day, interval=7)

        assert list(gen) == [
            datetime.date(2018, 1, 30),
            datetime.date(2018, 1, 29),

            datetime.date(2018, 1, 26),
            datetime.date(2018, 1, 25),
            datetime.date(2018, 1, 24),
        ]

    def test_get_missing_working_days(self, db):
        day = datetime.date(2018, 1, 31)
        base_currency = BaseCurrency(currency='EUR', date=datetime.date(2018, 1, 26))
        db.session.add(base_currency)
        db.session.commit()

        gen = BaseCurrency.get_missing_working_days(day, interval=7, base='EUR')

        assert list(gen) == [
            datetime.date(2018, 1, 30),
            datetime.date(2018, 1, 29),

            datetime.date(2018, 1, 25),
            datetime.date(2018, 1, 24),
        ]
