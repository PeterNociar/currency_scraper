import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import logging
from .extensions import db

logger = logging.getLogger(__name__)


class BaseCurrency(db.Model):
    __tablename__ = 'base_currency'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    currency = db.Column(db.String(3), index=True)
    date = db.Column(db.Date, index=True)
    rates = db.relationship('CurrencyRate')

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

        try:
            date = datetime.datetime.strptime(data.get('date'), "%Y-%m-%d").date()
            timestamp = datetime.datetime.fromtimestamp(data.get('timestamp'))
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
            logger.error(f'{__name__} encountered exception : {str(e)}')
            return None

        for currency, rate in data.get('rates', {}).items():
            try:
                currency_rate = CurrencyRate(currency=currency, rate=rate)
                base_currency.rates.append(currency_rate)
                db.session.add(currency_rate)
                db.session.commit()
            except (IntegrityError, Exception) as e:
                db.session.rollback()
                logger.info(f'currency {currency} for base_currency {base_currency} '
                            f'already exists for day {base_currency.date}')


class CurrencyRate(db.Model):
    __tablename__ = 'currency_rate'

    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(3))
    rate = db.Column(db.Numeric)
    base_currency_id = db.Column(db.Integer, db.ForeignKey('base_currency.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('currency', 'base_currency_id'),
    )

    def __repr__(self):
        return f'CurrencyRate base_id: {self.base_currency_id} currency: {self.currency}, rate: {self.rate}'
