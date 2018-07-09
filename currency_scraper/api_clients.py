from collections.abc import Mapping
from json import JSONDecodeError
import logging
import requests

logger = logging.getLogger(__name__)


class ResponseDict(Mapping):
    """
    Response object for Api clients
    """

    def __init__(self, *args, _error=None, _meta=None, **kwargs):
        if _error is None:
            self._error_dict = {}
        else:
            self._error_dict = _error

        if _meta is None:
            self._meta_dict = {}
        else:
            self._meta_dict = _meta

        self._storage = dict(*args, **kwargs)

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError(name)

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

    def __getitem__(self, key):
        return self._storage[key]

    def __setitem__(self, key, value):
        self._storage[key] = value

    @property
    def error(self):
        return self._error_dict

    def __str__(self):
        return f'{self._storage} - error: {self.error}'

    def __dict__(self):
        return self._storage


class FixerApiClient:
    """
    Api client for Fixer.io
    """

    def __init__(self, host, api_key):
        """

        :param host:
        :param api_key:
        """
        self.host = host
        self.api_key = api_key

    @classmethod
    def check_error_response(cls, response):
        """
        Checks for errors in client responses
        :param response:
        :return: ResponseDict
        """
        if response.status_code in (200, 201, 202, 203, 204):
            try:
                json_resp = response.json()
                logger.info(f'{cls.__name__} response : {resp}')
                return ResponseDict(json_resp)
            except JSONDecodeError:
                return ResponseDict({})
        else:
            error = {
                'message': f'{cls.__name__} request failed with'
                           f' status {response.status_code} headers: {response.headers}',
            }
            return ResponseDict(_error=error)

    def get_rates(self, date='latest'):
        """
        Retrieve currency rates for given day
        :param date:  Date for the currency rates
        :return: dictionary of rates for a base currency
        """

        url = f'{self.host}{date}'
        return self.check_error_response(requests.get(url=url, params={'access_key': self.api_key}))
