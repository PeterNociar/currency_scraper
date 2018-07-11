# -*- coding: utf-8 -*-
""" API Clients """

import os
import click

from currency_scraper.config import PROJECT_ROOT

TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """Run the tests."""
    import pytest

    rv = pytest.main([TEST_PATH, '--verbose'])
    exit(rv)
