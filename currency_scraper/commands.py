import os
import click

from currency_scraper.config import PROJECT_ROOT
from currency_scraper.extensions import scheduler

TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """Run the tests."""
    import pytest

    rv = pytest.main([TEST_PATH, '--verbose'])
    exit(rv)


@click.command()
def run_scheduler():
    """Run scheduler."""
    # create_app()
    # scheduler.start()
    x = 1
