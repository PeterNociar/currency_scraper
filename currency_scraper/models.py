# -*- coding: utf-8 -*-
"""Models"""

import datetime

from flask.globals import current_app as app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .extensions import db


class BaseCurrency(db.Model):
    """ Base Currency model """

    __tablename__ = 'base_currency'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    currency = db.Column(db.String(3), index=True)
    date = db.Column(db.Date, index=True)
    rates = db.relationship('CurrencyRate', cascade='all,delete')

    @classmethod
    def imgest_daily_data(cls, data):
        """
        Ingest daily data
        example data:
        {
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

        :param data:
        :return:
        """

        app.logger.debug(f'Data received: {data}')
        date_string = data['date']

        date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        timestamp = datetime.datetime.fromtimestamp(data.get('timestamp'))
        try:
            base_currency = cls.query.filter_by(currency=data.get('base'), date=date).one()
        except NoResultFound:
            base_currency = BaseCurrency(
                timestamp=timestamp,
                currency=data.get('base'),
                date=date,
            )
            db.session.add(base_currency)
            db.session.commit()
        except MultipleResultsFound as e:
            app.logger.error(f'{__name__} encountered exception : {str(e)}')
            return None

        for currency, rate in data.get('rates', {}).items():
            try:
                currency_rate = CurrencyRate(currency=currency, rate=rate)
                base_currency.rates.append(currency_rate)
                db.session.add(currency_rate)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                app.logger.info(f'currency {currency} for base_currency {base_currency} '
                                f'already exists for day {base_currency.date}')

        def __repr__(self):
            return f'BaseCurrency {self.currency} {self.date}'

    @classmethod
    def _get_working_days(cls, day, interval):
        """
        Return week days between day and interval number of days in the past

        :param day: Date
        :param interval: num of days
        :return: generator of day
        """
        for i in range(interval):
            day = day - datetime.timedelta(days=1)
            # Weekdays only
            if day.weekday() >= 5:
                continue

            yield day

    @classmethod
    def get_missing_working_days(cls, day, interval, base):
        """
        Return a days of week that doesnt have a record in BaseCurrency

        :param day: Date
        :param interval: num of days
        :param base: Base currency
        :return: generator
        """
        for day in cls._get_working_days(day, interval):
            if cls.query.filter_by(date=day, currency=base).first():
                continue
            yield day


class CurrencyRate(db.Model):
    """Currency Rate model"""

    __tablename__ = 'currency_rate'

    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(3))
    rate = db.Column(db.Numeric)
    base_currency_id = db.Column(db.Integer, db.ForeignKey('base_currency.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('currency', 'base_currency_id'),
    )

    def __repr__(self):
        return f'CurrencyRate base_id: {self.base_currency_id} ' \
               f'currency: {self.currency}, rate: {self.rate}'
