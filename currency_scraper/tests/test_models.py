import pytest

from currency_scraper.models import BaseCurrency, CurrencyRate


@pytest.mark.usefixtures('db')
class TestModels:

    def test_imgest_daily_data_success(self):
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

        BaseCurrency.imgest_daily_data(data=response_json)

        base_currencies = list(BaseCurrency.query.all())

        assert len(base_currencies) == 1
        assert base_currencies[0].currency == response_json['base']
        assert base_currencies[0].date.isoformat() == response_json['date']

        currency_rates = list(CurrencyRate.query.all())
        assert len(currency_rates) == 3
        for rate in currency_rates:
            assert float(rate.rate) == response_json['rates'][rate.currency]

    def test_imgest_daily_data_duplicate_error(self):
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

        BaseCurrency.imgest_daily_data(data=response_json)
        BaseCurrency.imgest_daily_data(data=response_json)

        currency_rates = list(CurrencyRate.query.all())

        assert len(currency_rates) == 3
        for rate in currency_rates:
            assert float(rate.rate) == response_json['rates'][rate.currency]
