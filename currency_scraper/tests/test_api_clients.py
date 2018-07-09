import pytest
import responses

from currency_scraper.api_clients import ResponseDict, FixerApiClient


@pytest.mark.usefixtures('db')
class TestClients:

    def test_response_dict_succes(self):
        response = ResponseDict({'a': 1, 'b': '2'})
        assert response.a == 1
        assert response.b == '2'

    def test_response_dict_error(self):
        response = ResponseDict(_error={'error': ''})
        assert response.error == {'error': ''}

    @responses.activate
    def test_check_success_response(self):
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

        base_url = 'http://baseurl/api/'
        api_key = '1234567'
        responses.add(responses.GET, f'{base_url}latest', json=response_json, status=200)

        client = FixerApiClient(host=base_url, api_key=api_key)
        resp = client.get_rates()

        assert dict(resp) == response_json
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == f'{base_url}latest'

    @responses.activate
    def test_check_success_response(self):
        base_url = 'http://baseurl/api/'
        api_key = '1234567'
        responses.add(responses.GET, f'{base_url}latest', json={}, status=404)

        client = FixerApiClient(host=base_url, api_key=api_key)
        resp = client.get_rates()

        assert dict(resp) == {}
        assert len(responses.calls) == 1
        assert resp.error == {'message': 'FixerApiClient request failed with status 404 headers: '"{'Content-Type': 'application/json'}"}
