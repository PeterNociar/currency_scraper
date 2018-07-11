# -*- coding: utf-8 -*-
""" Admin """

from flask_admin.base import Admin
from flask_admin.contrib.sqla.view import ModelView

from currency_scraper.extensions import db
from currency_scraper.models import BaseCurrency, CurrencyRate


def register_admin(app):
    """ Register admin views """
    admin = Admin(app, name='Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(BaseCurrency, db.session))
    admin.add_view(ModelView(CurrencyRate, db.session))
